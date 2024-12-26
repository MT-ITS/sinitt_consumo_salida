from flask import session, g
from flask_login import current_user
import json
from datetime import datetime
from session_manager.stateful_session_manager import StatefulSessionManager
import uuid
import logging
from datetime import timedelta


def renew_session():
    """
    Realiza la renovación de la sesión cuando esta se ha caido
    :return:
    """
    session.permanent = True
    # app.permanent_session_lifetime = timedelta(minutes=5)
    session.modified = True
    g.user = current_user


def open_session(json_payload):
    """
    Realiza la apertura de la sesión de DATEX-II cuando se inicia el servidor.

    :param json_payload: json para el inicio de la sesión.
    :return:
    """
    try:
        # Load from DPayload the agency to check and generate session id
        ex_info = json_payload['exchangeInformation']
        # logging.info(exInfo)
        ex_context = ex_info['ExchangeContext']
        # Create Exchange Context Object
        if 'name' in ex_context['supplierOrCisRequester']:
            session['agency_name'] = ex_context['supplierOrCisRequester']['name']
            ex_info = ExchangeContext(ex_context['codedExchangeProtocol'], ex_context['exchangeSpecificationVersion'],
                                      ex_context['supplierOrCisRequester']['name'])
        elif 'internationalIdentifier' in ex_context['supplierOrCisRequester']:
            session['agency_name'] = ex_context['supplierOrCisRequester']['internationalIdentifier'][
                'nationalIdentifier']
            ex_info = ExchangeContext(ex_context['codedExchangeProtocol'], ex_context['exchangeSpecificationVersion'],
                                      ex_context['supplierOrCisRequester']['internationalIdentifier']['country'],
                                      ex_context['supplierOrCisRequester']['internationalIdentifier'][
                                          'nationalIdentifier'])
        else:
            # Empty response
            logging.info('Ingest Action: 213 - Agencia no identificada /openSession')
            return False, failed_process_status(ex_info, 'No se pudo abrir la sesión a agencia no identificada',
                                                DynamicInformation.ES_OFFLINE)
        # Create Dynamic Info Object
        session_id = str(uuid.uuid4())
        dyn_object = DynamicInformation("online", session_id, "ack")

        # Join to create exchange Information object
        exchange_info = exchangeInformation(ex_info, dyn_object)
        session['session_info'] = dyn_object.sessionInformation
        logging.info(session['session_info'])
        session['exchange_info'] = exchange_info.to_json()
        session.permanent = True
        session.permanent_session_lifetime = timedelta(minutes=6)

        # Apertura de sesión en BD
        stateful_manager = StatefulSessionManager()
        stateful_manager.open_session(session_id, session['agency_name'], str(get_current_date()))
        logging.info('Ingest Action: 115 - Client Status ON /openSession - Agencia: %s', session['agency_name'])
        return True, exchange_info.to_json()
    except Exception as e:
        # Two cases, malformed JSON & wrong return
        logging.info(e)
        logging.info('Error de apertura de sesión: la estructura del mensaje Datex no es correcto')
        logging.info('Ingest Action: 208 - Fail on open session  /openSession')
        return False, failed_process_status(ex_info, 'La estructura del mensaje Datex no es correcta ',
                                            DynamicInformation.ES_OFFLINE)


def return_agency(json_payload):
    """
    Verifica en el json de entrada y obtiene la agencia desde la cual se llevaran a cabo
    la conexión

    :param json_payload:  json para el inicio de la sesión.
    :return:
    """
    try:
        logging.info("Entering return_agency")
        # Load from DPayload the agency to check and generate session id
        exInfo = json_payload['exchangeInformation']
        # logging.info(exInfo)
        ex_context = exInfo['ExchangeContext']
        # Create Exchange Context Object
        if 'name' in ex_context['supplierOrCisRequester']:
            return ex_context['supplierOrCisRequester']['name']
        elif 'internationalIdentifier' in ex_context['supplierOrCisRequester']:
            return ex_context['supplierOrCisRequester']['internationalIdentifier']['nationalIdentifier']
        else:
            return 'No Agency'
    except Exception as e:
        # Two cases, malformed JSON & wrong return
        logging.info(e)
        return 'Agency error'


def close_session(json_payload):
    """
    Realiza el cierre de la sesión de DATEX-II cuando se termina el servidor.

    :param json_payload: Json utilizado para el cierre de la sesión.
    :return:
    """
    try:
        # Load from DPayload the agency to check and generate session id
        ex_info = json_payload['exchangeInformation']
        # logging.info(exInfo)
        ex_context = ex_info['ExchangeContext']
        # Create Exchange Context Object
        if 'name' in ex_context['supplierOrCisRequester']:
            session['agency_name'] = ex_context['supplierOrCisRequester']['name']
            exchange_info = ExchangeContext(ex_context['codedExchangeProtocol'],
                                            ex_context['exchangeSpecificationVersion'],
                                            ex_context['supplierOrCisRequester']['name'])
        elif 'internationalIdentifier' in ex_context['supplierOrCisRequester']:
            session['agency_name'] = ex_context['supplierOrCisRequester']['internationalIdentifier'][
                'nationalIdentifier']
            exchange_info = ExchangeContext(ex_context['codedExchangeProtocol'],
                                            ex_context['exchangeSpecificationVersion'],
                                            ex_context['supplierOrCisRequester']['internationalIdentifier']['country'],
                                            ex_context['supplierOrCisRequester']['internationalIdentifier'][
                                                'nationalIdentifier'])
        else:
            logging.info('Ingest Action: 213 - Agencia no identificada  /closeSession')
            # Empty response
            return False, ex_info

        # Create Dynamic Info Object
        session_id = ex_info['DynamicInformation']['sessionInformation']['sessionID']
        dyn_object = DynamicInformation("offline", session_id, "ack")

        # Join to create exchange Information object
        exc_info = exchangeInformation(exchange_info, dyn_object)
        # session.pop('session_info')
        # session.pop('exchange_info')

        # Apertura de sesión en BD
        stateful_manager = StatefulSessionManager()
        stateful_manager.close_session(session_id)
        logging.info('Ingest Action: 112 - Client Status OFF  /closeSession  - Agencia: %s', session['agency_name'])
        return True, exc_info.to_json()
    except Exception as e:
        # Two cases, malformed JSON & wrong return
        logging.error(e)
        logging.info(exc_info)
        logging.info('Ingest Action: 212 - Fail on close session /closeSession')
        return False, failed_process_status(exc_info.to_json(), 'Error desconocido', DynamicInformation.ES_UNDEFINED)
    return 'Session not set'


def keep_alive(dPayload):
    """
    Mediante esta función se realiza el envio de un mensaje keep alive para mantener contectado
    al servidor con el nodo DATEX-II de entrega de información.

    :param dPayload:
    :return:
    """
    try:
        exchangeinfo = dPayload['exchangeInformation']
        ex_context = exchangeinfo['ExchangeContext']
        # logging.info(exchangeinfo)
        if check_active(exchangeinfo) == True:
            # Create Exchange Context Object
            if 'name' in ex_context['supplierOrCisRequester']:
                session['agency_name'] = ex_context['supplierOrCisRequester']['name']
                excInfo = ExchangeContext(ex_context['codedExchangeProtocol'],
                                          ex_context['exchangeSpecificationVersion'],
                                          ex_context['supplierOrCisRequester']['name'])
            elif 'internationalIdentifier' in ex_context['supplierOrCisRequester']:
                session['agency_name'] = ex_context['supplierOrCisRequester']['internationalIdentifier'][
                    'nationalIdentifier']
                excInfo = ExchangeContext(ex_context['codedExchangeProtocol'],
                                          ex_context['exchangeSpecificationVersion'],
                                          ex_context['supplierOrCisRequester']['internationalIdentifier']['country'],
                                          ex_context['supplierOrCisRequester']['internationalIdentifier'][
                                              'nationalIdentifier'])
            else:
                # Empty response
                logging.info('Ingest Action: 213 - Agencia no identificada en /keepAlive')
                return False, failed_process_status(exchangeinfo,
                                                    'No existe identificador de agencia en el nodo supplierOrCisRequester',
                                                    DynamicInformation.ES_UNDEFINED)

            # Create Dynamic Info Object
            session_id = exchangeinfo['DynamicInformation']['sessionInformation']['sessionID']
            dyn_object = DynamicInformation(DynamicInformation.ES_ONLINE, session_id, "ack")

            # Join to create exchange Information object
            excInfo = exchangeInformation(excInfo, dyn_object)
            # logging.info(excInfo.toJson())
            logging.info('Ingest Action: 115 - Client Status ON /keepAlive - Agencia: %s', session['agency_name'])
            return True, excInfo.to_json()
        else:
            logging.info(exchangeinfo)
            logging.info('Ingest Action: 114 - Client Status OFF /keepAlive')
            return False, not_active_session(exchangeinfo)
    except Exception as e:
        logging.info(e)
        logging.info('Ingest Action: 214 - Fail on keep alive /keepAlive')
        return False, failed_process_status(exchangeinfo, 'La estructura del mensaje Datex no es correcta',
                                            DynamicInformation.ES_UNDEFINED)


def check_active(exchange_info):
    """
    Verifica que la sesión se mantenga activa.

    :param exchange_info:
    :return:
    """

    try:
        logging.info('Checking session')
        # Check if session is active
        if 'DynamicInformation' in exchange_info:
            if 'sessionInformation' in exchange_info['DynamicInformation']:
                '''
                logging.info('get session ID')
                logging.info(session)
                logging.info(session['session_info'])
                logging.info(exchange_info['DynamicInformation']['sessionInformation'])
                logging.info(exchange_info['DynamicInformation']['sessionInformation']['sessionID'])
                if session['session_info']['sessionID'] == exchange_info['DynamicInformation']['sessionInformation'][
                    'sessionID']:
                    logging.info('sessions equal')
                    return True
                '''

                # Apertura de sesión en BD
                stateful_manager = StatefulSessionManager()
                active_sesion = stateful_manager.query_if_session_active(exchange_info['DynamicInformation']
                                                                         ['sessionInformation']['sessionID'])
                if active_sesion is not None:
                    logging.info('sessions exists')
                    return True
        logging.info('Not equal')
        return False
    except Exception as e:
        logging.info('Exception checking active')
        logging.info(e)
        return False
    return true


def not_active_session(exchangeinfo):
    """
    Construye el json para cuando se detecta que la sesión no está activa

    :param exchangeinfo:
    :return:
    """
    logging.info('Not active session: ' + json.dumps(exchangeinfo))
    dyn_object = DynamicInformation(DynamicInformation.ES_OFFLINE, None, "fail")
    exchangeinfo['DynamicInformation'] = json.loads(dyn_object.to_json())
    exchangeinfo['DynamicInformation'].pop('sessionInformation', None)
    exchangeinfo['DynamicInformation']['returnInformation']['returnStatusReason'] = status_reason(
        "No existe una sesión activa", "es")
    # logging.info(json.dumps(exchangeinfo))
    resp = {'exchangeInformation': exchangeinfo}
    # logging.info(json.dumps(resp))
    return json.dumps(resp)


def failed_process_status(exchangeinfo, failed_process_reason, status):
    """
    Construye el json a enviar cuando el proceso quedo en estado de error.

    :param exchangeinfo:
    :param failed_process_reason:
    :param status:
    :return:
    """
    logging.info(exchangeinfo)
    if 'sessionInformation' in exchangeinfo['DynamicInformation']:
        session_id = exchangeinfo['DynamicInformation']['sessionInformation']['sessionID']
        dyn_object = DynamicInformation(status, session_id, "fail")
    else:
        dyn_object = DynamicInformation(status, "fail")
    logging.info('Before dyn object')
    exchangeinfo['DynamicInformation'] = dyn_object.to_json()
    logging.info(exchangeinfo['DynamicInformation'])
    exchangeinfo['DynamicInformation'] = json.loads(dyn_object.to_json())
    logging.info('After dyn object')
    exchangeinfo['DynamicInformation']['returnInformation']['returnStatusReason'] = status_reason(failed_process_reason,
                                                                                                  "es")
    logging.info('Before resp ')
    resp = {'exchangeInformation': {'ExchangeContext': exchangeinfo['ExchangeContext'],
                                    'DynamicInformation': exchangeinfo['DynamicInformation']
                                    }}
    logging.info('After resp ')
    # logging.info(resp)
    return json.dumps(resp)


def succes_process_status(exchangeinfo, succes_reason):
    """
    Construye el json a enviar cuando el proceso quedo en estado de éxitoso.

    :param exchangeinfo:
    :param succes_reason:
    :return:
    """
    # logging.info('Not active session: '+json.dumps(exchangeinfo))
    session_id = exchangeinfo['DynamicInformation']['sessionInformation']['sessionID']
    dyn_object = DynamicInformation("online", session_id, "ack")
    exchangeinfo['DynamicInformation'] = json.loads(dyn_object.to_json())
    exchangeinfo['DynamicInformation']['returnInformation']['returnStatusReason'] = status_reason(succes_reason, "es")
    logging.info('Before resp ')
    resp = {'exchangeInformation': {'ExchangeContext': exchangeinfo['ExchangeContext'],
                                    'DynamicInformation': exchangeinfo['DynamicInformation']
                                    }}
    return json.dumps(resp)


def status_reason(reason, language):
    """
    Construye la porción del json para entrega el estado del proceso.

    :param reason:
    :param language:
    :return:
    """
    statusReason = []
    statusReasonEsp = {}
    statusReasonEsp['lang'] = language
    statusReasonEsp['value'] = reason
    statusReason.append(statusReasonEsp)
    return statusReason


def get_current_date():
    """
    Obtiene la fecha y hora actual en cadena de caracteres
    :return:
    """
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%Y-%m-%dT%H:%M:%S.%f")
    return timestampStr


class DynamicInformation():
    """
    CLase para representar la sesión y su estado.

    """
    ES_CLOSING_SESSION = "closingSession"
    ES_OPENING_SESSION = "openingSession"
    ES_RESUMING = "resuming"
    ES_OFFLINE = "offline"
    ES_ONLINE = "online"
    ES_UNDEFINED = "undefined"

    class sessionInformation():
        def __init__(self, session_id):
            self.startSession = get_current_date()
            self.sessionID = session_id

        def to_json(self):
            return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    class returnInformation():
        ACK_RETURN = 'ack'
        CLOSE_SESSION_REQ_RETURN = 'closeSessionRequest'
        FAIL_RETURN = 'fail'
        SNAP_SYNC_RETURN = 'snapshotSynchronisationRequest'

        def __init__(self, status):
            self.returnStatus = status

        def to_json(self):
            return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def __init__(self, *args):
        if len(args) == 3:
            self.exchangeStatus = args[0]
            self.messageGenerationTimestamp = get_current_date()
            self.sessionInformation = self.sessionInformation(args[1]).__dict__
            self.returnInformation = self.returnInformation(args[2]).__dict__

        elif len(args) == 2:
            self.exchangeStatus = args[0]
            self.messageGenerationTimestamp = get_current_date()
            self.returnInformation = self.returnInformation(args[1]).__dict__

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class ExchangeContext():
    """
    Clase para representar el contexto de intercambio definido pro DATEX-II.
    """
    class supplierOrCisRequester():
        def __init__(self, *args):
            # countr, nationalidentity):
            if len(args) == 2:
                logging.info('Init supCisReq')
                self.internationalIdentifier = {}
                self.internationalIdentifier['country'] = args[0]
                self.internationalIdentifier['nationalIdentifier'] = args[1]
            elif len(args) == 1:
                self.name = args[0]

        def to_json(self):
            return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def __init__(self, *args):
        # protocol, exSpecifitacionVersion, countr, nationalidentity):
        if len(args) == 4:
            logging.info('Init Exchang Context 1')
            self.codedExchangeProtocol = args[0]
            self.exchangeSpecificationVersion = args[1]
            self.supplierOrCisRequester = self.supplierOrCisRequester(args[2], args[3]).__dict__
        elif len(args) == 3:
            self.codedExchangeProtocol = args[0]
            self.exchangeSpecificationVersion = args[1]
            self.supplierOrCisRequester = self.supplierOrCisRequester(args[2]).__dict__

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class exchangeInformation():
    """
    Clase para representar la información de intercambio definido pro DATEX-II.
    """
    def __init__(self, ex_context, dynamic_inf):
        self._modelVersion = '3'
        self.ExchangeContext = ex_context.__dict__
        self.DynamicInformation = dynamic_inf.__dict__

    def include_key(self, o):
        elem = {}
        elem[o.__class__.__name__] = o.__dict__
        return elem

    def to_json(self):
        return json.dumps(self, default=self.include_key, sort_keys=True, indent=4)
