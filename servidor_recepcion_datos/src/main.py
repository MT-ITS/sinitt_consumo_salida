# -*- coding: utf-8 -*-
"""Used Modules."""
import logging
import logging.config
from datetime import timedelta
from time import perf_counter
import json
import sys
from flask import Flask, request
from flask_session import Session
from session_manager import session_manager
from validator.validator import process_message
from multiprocessing import Process
from settings import settings
from flask_sqlalchemy import SQLAlchemy

sys.path.insert(0, "libs")

app = Flask(__name__)
app.config["SESSION_TYPE"] = "sqlalchemy"
app.config["SQLALCHEMY_DATABASE_URI"] = settings.sqlalchemy_pg
app.config["SESSION_SQLALCHEMY_TABLE"] = settings.sqlalchmey_session_table
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_POOL_RECYCLE"] = 660
app.config["SQLALCHEMY_POOL_SIZE"] = 30

db = SQLAlchemy(app)
session = Session(app)
session.app.session_interface.db.create_all()

Log_Format = " Ingest-Server - %(asctime)s - %(name)s - %(levelname)s - %(message)s"

logging.basicConfig(  # filename = "logs/servidor_recepcion_datos.log",
    stream=sys.stdout,
    # filemode = "a",
    level=logging.INFO,
    format=Log_Format,
    force=True,
)

app.secret_key = settings.secret_key
app.permanent = True
app.permanent_session_lifetime = timedelta(minutes=6)
app.session_refresh_each_request = True


@app.before_request
def func():
    session_manager.renew_session


def well_formed_container(payload, d_payload, version="3.1"):
    """Uses process_message in the payload."""
    is_valid, return_message, json_message = process_message(
        d_payload, payload, settings.DATEX_MESSAGE_CONTAINER, version
    )
    return is_valid, return_message, json_message


def enrich_json(json_original, agencia, d_payload):
    """fills up a json."""
    json_str_r = {}
    json_str_r["filterAttributes"] = {}
    json_str_r["filterAttributes"]["agency"] = agencia
    json_str_r["filterAttributes"]["datexMessageType"] = d_payload
    json_str_r["datexPublicationData"] = json_original
    return json_str_r


def separar_json(**kwargs):
    global i
    separacion_start = perf_counter()
    logging.info("Inicio de proceso de separación")
    dpayload = kwargs.get("d_payload", {})
    payload = kwargs.get("sample_payload", {})
    version = kwargs.get("version", {})

    logging.info("Starting separation")

    """Dividing datex II json."""
    if version == "3.5":
        """Dividing datex II json."""
        d_pay = {
            "roaMeasuredDataPublication": "siteMeasurements",
            "roaElaboratedDataPublication": "physicalQuantity",
            "sitSituationPublication": "situation",
            "roaMeasurementSiteTablePublication": "measurementSiteTable",
            "locationReferencingPredefinedLocationsPublication": "predefinedLocationReference"
        }
        # d_payloads sirve para hacer un mapeo entre la url del api y el key con el que está la publicacion en mongodb.
        d_payloads = {
            "elaboratedDataPublication": "roaElaboratedDataPublication",
            "measuredDataPublication": "roaMeasuredDataPublication",
            "measuredSiteTablePublication": "roaMeasurementSiteTablePublication",
            "vmsPublication": "vmsVmsPublication",
            "predefinedLocationsPublication": "locationReferencingPredefinedLocationsPublication",
            "situationPublication": "sitSituationPublication",
        }
    else:
        d_pay = {
            "roadTrafficDataMeasuredDataPublication": "siteMeasurements",
            "situationPublication": "situation",
            "roadTrafficDataMeasurementSiteTablePublication": "measurementSiteTable",
            "locationReferencingPredefinedLocationsPublication": "predefinedLocationReference"
        }
        d_payloads = {
            "elaboratedDataPublication": "roadTrafficDataElaboratedDataPublication",
            "measuredDataPublication": "roadTrafficDataMeasuredDataPublication",
            "MeasuredSiteTablePublication": "roadTrafficDataMeasurementSiteTablePublication",
            "vmsPublication": "vmsVmsPublication",
            "PredefinedLocationsPublication": "locationReferencingPredefinedLocationsPublication",
            "situationPublication": "situationPublication",
        }

    logging.info("dpayload=" + str(dpayload))
    n_temp = ""
    for name in d_payloads:
        if name.lower() == dpayload.lower():
            n_temp = name
    name = d_payloads[n_temp]

    logging.info("PAYLOAD:" + str(payload))
    logging.info("NAME:" + str(name))
    logging.info("dpay[name}:" + str(d_pay[name]))

    element_list = payload[name][d_pay[name]]
    if d_pay[name] == "measurementSiteTable":
        logging.info("in measurementSiteTable")
        logging.info(d_pay[name])
        logging.info(payload[name][d_pay[name]])
        logging.info(payload[name][d_pay[name]][0])
        element_list = payload[name][d_pay[name]][0]["measurementSite"]
        logging.info('element List')
        logging.info(element_list)
        for i, _ in enumerate(element_list):
            # Prueba de numero
            new_json = payload
            new_json[name][d_pay[name]][0]["measurementSite"] = [element_list[i]]
            logging.info("New JSON")
            logging.info(new_json)
    else:
        logging.info("into else")
        for i, _ in enumerate(element_list):
            logging.info("valor de i del for: " + str(i))
            # Prueba de numero
            new_json = payload
            new_json[name][d_pay[name]] = [element_list[i]]
            logging.info("New JSON")
            logging.info(new_json)

    logging.info("Separated " + str(i + 1) + " elements for persistance")
    separacion_end = perf_counter()
    logging.info("Fin de proceso de separación")
    logging.info("Tiempo de separación: " + str(separacion_end - separacion_start))


@app.route("/v35/<d_payload>/putData", methods=["POST"])
def put_data_v35(d_payload):
    """POST request of data payload."""
    """POST request of data payload."""
    try:
        datex_payload = request.data
        msg_cont = json.loads(datex_payload)
        logging.info("put data v35")
        logging.info('payload: ' + str(msg_cont))
        well_formed, return_message, json_message = well_formed_container(
            msg_cont, d_payload, "3.5"
        )

        logging.info("el valor de well_formed es:")
        logging.info(well_formed)
        if well_formed is True:
            exchangeinfo = msg_cont["exchangeInformation"]
            payload = msg_cont["payload"]
            logging.info("Session check")
            if session_manager.check_active(exchangeinfo) is True:
                # Session is active
                logging.info('in check_active check_active')
                agencia = session_manager.return_agency(msg_cont)
                logging.info('agency:' + str(agencia))

                # Aqui se debe colocar el código que se deba ejecutar como parte
                # de la respuesta a la llegada de un nuevo mensaje. la variable payload tiene el
                # valor.
                print(payload)

                response = (
                    session_manager.succes_process_status(
                        exchangeinfo, "Dato es válido y ha sido registrado"
                    ),
                    200,
                    {"Content-Type": "application/json"},
                )
                logging.info('Ingest Action: 119 - response put data 200 /putData - Agencia:' + agencia)
            else:
                # Session is not active
                logging.info("No session")
                response = (
                    session_manager.not_active_session(exchangeinfo),
                    401,
                    {"Content-Type": "application/json"},
                )
                logging.info('Ingest Action: 119 - response put data 401 /putData_v35: ' + str(d_payload))
        else:
            logging.info("Info exchange")
            exchangeinfo = msg_cont["exchangeInformation"]
            if exchangeinfo is not None:
                logging.info("Persisting error to db")
                response = (
                    session_manager.failed_process_status(
                        exchangeinfo,
                        "La estructura del mensaje Datex no es correcto ",
                        session_manager.DynamicInformation.ES_ONLINE,
                    ),
                    400,
                    {"Content-Type": "application/json"},
                )
                logging.info('Ingest Action: 119 - response put data 400 /putData')
            else:
                response = (
                    "Datex message was not correctly formed",
                    400,
                    {"Content-Type": "application/json"},
                )
                logging.info('Ingest Action: 119 - response put data 400 /putData_v35: ' + str(d_payload))
        return response
    except Exception as exp:
        logging.error(exp)
        logging.info('Ingest Action: 209 - fail on put data 500 /putData_v35: ' + str(d_payload))
        return "Put data exception", 500, {"Content-Type": "application/json"}


@app.route("/<d_payload>/putData", methods=["POST"])
def put_data(d_payload):
    """POST request of data payload."""
    datex_payload = request.data
    try:
        datex_payload = datex_payload.decode('latin-1')
        msg_cont = json.loads(datex_payload.encode('utf-8'))
        logging.info("Before well formed", msg_cont)
        well_formed, return_message, json_message = well_formed_container(
            msg_cont, d_payload
        )
        logging.info(well_formed)
        if well_formed is True:
            exchangeinfo = msg_cont["exchangeInformation"]
            payload = msg_cont["payload"]
            logging.info("Session check")

            if session_manager.check_active(exchangeinfo) is True:
                # Session is active
                logging.info('entro en check_active:' + str(msg_cont))
                agencia = session_manager.return_agency(msg_cont)
                logging.info('agency:' + str(agencia))

                # Aqui se debe colocar el código que se deba ejecutar como parte
                # de la respuesta a la llegada de un nuevo mensaje.

                response = (
                    session_manager.succes_process_status(
                        exchangeinfo, "Dato es válido y ha sido registrado"
                    ),
                    200,
                    {"Content-Type": "application/json"},
                )
                logging.info('Ingest Action: 119 - response put data 200 /putData - Agencia:' + agencia)
            else:
                # Session is not active
                logging.info("No session")
                response = (
                    session_manager.not_active_session(exchangeinfo),
                    401,
                    {"Content-Type": "application/json"},
                )
                logging.info('Ingest Action: 119 - response put data 401 /putData')
        else:
            print('the message is not well formed')
            exchangeinfo = msg_cont["exchangeInformation"]
            logging.info("Info exchange")
            if exchangeinfo is not None:
                logging.info("Persisting error to db")
                response = (
                    session_manager.failed_process_status(
                        exchangeinfo,
                        "La estructura del mensaje Datex no es correcto ",
                        session_manager.DynamicInformation.ES_ONLINE,
                    ),
                    400,
                    {"Content-Type": "application/json"},
                )
                logging.info('Ingest Action: 119 - response put data 400 /putData')
            else:
                response = ("Datex message was not correctly formed",
                            200,
                            {"Content-Type": "application/json"},
                            )
        logging.info('Ingest Action: 119 - response put data 400 /putData')
        return response
    except Exception as exp:
        logging.error(exp)
        logging.info('Ingest Action: 209 - fail on put data 500 /putData')
        if 'datex_payload' in vars():
            logging.info('datex_payload:', datex_payload)
        return "Put data exception", 500, {"Content-Type": "application/json"}


@app.route("/v35/<d_payload>/putSnapShotData", methods=["POST"])
def put_snapshot_data_v35(d_payload):
    """POST request of Snapshot data payload."""
    logging.info("Put Snapshot data data v35 execution ...")
    try:
        datex_payload = request.data
        msg_cont = json.loads(datex_payload)
        logging.info('payload: ' + str(msg_cont))
        well_formed, return_message, json_message = well_formed_container(
            msg_cont, d_payload, "3.5"
        )
        logging.info(well_formed)
        # logging.info(return_message)
        # logging.info(json_message)
        if well_formed is True:
            exchangeinfo = msg_cont["exchangeInformation"]
            payload = msg_cont["payload"]
            logging.info("Session check")
            if session_manager.check_active(exchangeinfo) is True:
                # Session is active
                agencia = session_manager.return_agency(msg_cont)

                # Aquí se debe colocar el código que se deba ejecutar como parte
                # de la respuesta a la llegada de un nuevo mensaje.
                print(payload)

                response = (
                    session_manager.succes_process_status(
                        exchangeinfo, "Dato es válido y ha sido registrado"
                    ),
                    200,
                    {"Content-Type": "application/json"},
                )
                logging.info(
                    'Ingest Action: 117 - response put snapshot data 200 /putSnapShotData - Agencia: ' + agencia)
            else:
                # Session is not active
                logging.info("No session")
                response = (
                    session_manager.not_active_session(exchangeinfo),
                    401,
                    {"Content-Type": "application/json"},
                )
                logging.info('Ingest Action: 117 - response put snapshot data 401 /putSnapShotData: ' + str(d_payload))
        else:
            exchangeinfo = msg_cont["exchangeInformation"]
            logging.info("Info exchange")
            if exchangeinfo is not None:
                logging.info("Persisting error to db")
                response = (
                    session_manager.failed_process_status(
                        exchangeinfo,
                        "La estructura del mensaje Datex no es correcto ",
                        session_manager.DynamicInformation.ES_ONLINE,
                    ),
                    400,
                    {"Content-Type": "application/json"},
                )
                logging.info(
                    'Ingest Action: 211 - Fail on put SnapshotData -- Client Status OFF /putSnapShotData: ' + str(
                        d_payload))
            else:
                response = (
                    "Datex message was not correctly formed",
                    400,
                    {"Content-Type": "application/json"},
                )
                logging.info(
                    'Ingest Action: 211 - Fail on put SnapshotData 400 -- Client Status OFF /putSnapShotData: ' + str(
                        d_payload))
        return response
    except Exception as exp:
        logging.error(exp)
        logging.info('Ingest Action: 211 - Fail on put SnapshotData 500 -- Client Status OFF /putSnapShotData: ' + str(
            d_payload))
        return "Put data exception", 500


@app.route("/<d_payload>/putSnapShotData", methods=["POST"])
def put_snapshot_data(d_payload):
    """POST request of Snapshot data payload."""
    logging.info("Put Snapshot data data execution...")
    try:
        datex_payload = request.data
        msg_cont = json.loads(datex_payload)
        logging.info("Before well formed")
        well_formed, return_message, json_message = well_formed_container(
            msg_cont, d_payload
        )
        logging.info(well_formed)
        if well_formed is True:
            exchangeinfo = msg_cont["exchangeInformation"]
            payload = msg_cont["payload"]
            logging.info("Session check")
            if session_manager.check_active(exchangeinfo) is True:
                # Session is active
                agencia = session_manager.return_agency(msg_cont)
                for items in payload:
                    print(items)
                    # Aca debe colocar el código que se desee como respuesta
                    # una vez llega la información.

                    # Las siguientes líneas comentadas son un ejemplo de un
                    # tratamiento de datos que se podría realizar con un proceso
                    # independiente.

                    # p = Process(target = separar_json, kwargs={"d_payload":d_payload,"sample_payload":items, "agencia":agencia})
                    # separar_json(d_payload=d_payload, sample_payload=items, agencia=agencia)
                    # p = Process(
                    #    target=separar_json,
                    #    kwargs={
                    #        "d_payload": d_payload,
                    #        "sample_payload": items,
                    #        "agencia": agencia,
                    #    },
                    # )
                    # p.start()

                response = (
                    session_manager.succes_process_status(
                        exchangeinfo, "Dato es válido y ha sido registrado"
                    ),
                    200,
                    {"Content-Type": "application/json"},
                )
                logging.info(
                    'Ingest Action: 117 - response put snapshot data 200 /putSnapShotData - Agencia: ' + agencia)
            else:
                # Session is not active
                logging.info("No session")
                response = (
                    session_manager.not_active_session(exchangeinfo),
                    401,
                    {"Content-Type": "application/json"},
                )
                logging.info('Ingest Action: 117 - response put snapshot data 401 /putSnapShotData')
        else:
            exchangeinfo = msg_cont["exchangeInformation"]
            logging.info("Info exchange")
            if exchangeinfo is not None:
                logging.info("Persisting error to db")
                # Se deberia implementar algún procesamiento en el evento
                # de recibir los mensajes con error. En las siguientes líneas
                # se debe colocar ese tratamiento

                response = (
                    session_manager.failed_process_status(
                        exchangeinfo,
                        "La estructura del mensaje Datex no es correcto ",
                        session_manager.DynamicInformation.ES_ONLINE,
                    ),
                    400,
                    {"Content-Type": "application/json"},
                )
                logging.info('Ingest Action: 211 - Fail on put SnapshotData -- Client Status OFF /putSnapShotData')
            else:
                response = (
                    "Datex message was not correctly formed",
                    400,
                    {"Content-Type": "application/json"},
                )
                logging.info('Ingest Action: 211 - Fail on put SnapshotData 400 -- Client Status OFF /putSnapShotData')
        return response
    except Exception as exp:
        logging.error(exp)
        logging.info(
            'Ingest Action: 211 - Fail on put SnapshotData 500 -- Client Status OFF /putSnapShotData')
        return "Put data exception", 500


@app.route("/v35/<d_payload>/keepAlive", methods=["POST"])
def keep_alive_v35(d_payload):
    """Using keep Alive function from session_manager in the payload."""
    datex_payload = request.data
    try:
        msg_cont = json.loads(datex_payload)
        is_valid, return_message, json_message = process_message(
            d_payload, msg_cont, settings.DATEX_MESSAGE_CONTAINER, "3.5"
        )
        logging.info(return_message)
        logging.info(json_message)
        if is_valid:
            k_ali, msg = session_manager.keep_alive(msg_cont)
            if k_ali is True:
                response = msg, 200, {"Content-Type": "application/json"}
            else:
                response = msg, 401, {"Content-Type": "application/json"}
        else:
            response = (
                session_manager.failed_process_status(
                    msg_cont["exchangeInformation"],
                    "La estructura del mensaje Datex no es correcto ",
                    session_manager.DynamicInformation.ES_UNDEFINED,
                ),
                400,
                {"Content-Type": "application/json"},
            )
        return response
    except Exception as exp:
        logging.error(exp)
        response = (
            session_manager.failed_process_status(
                msg_cont["exchangeInformation"],
                "Ocurrió un error al procesar el mensaje",
                session_manager.DynamicInformation.ES_UNDEFINED,
            ),
            500,
            {"Content-Type": "application/json"},
        )
        return response


@app.route("/<d_payload>/keepAlive", methods=["POST"])
def keep_alive(d_payload):
    """Using keep Alive function from session_manager in the payload."""
    try:
        datex_payload = request.data
        msg_cont = json.loads(datex_payload)
        is_valid, return_message, json_message = process_message(
            d_payload, msg_cont, settings.DATEX_MESSAGE_CONTAINER, "3.1"
        )
        logging.info(return_message)
        logging.info(json_message)
        if is_valid:
            k_ali, msg = session_manager.keep_alive(msg_cont)
            if k_ali is True:
                response = msg, 200, {"Content-Type": "application/json"}
            else:
                response = msg, 401, {"Content-Type": "application/json"}
        else:
            response = (
                session_manager.failed_process_status(
                    msg_cont["exchangeInformation"],
                    "La estructura del mensaje Datex no es correcto ",
                    session_manager.DynamicInformation.ES_UNDEFINED,
                ),
                400,
                {"Content-Type": "application/json"},
            )
        return response
    except Exception as exp:
        logging.error(exp)
        response = (
            session_manager.failed_process_status(
                msg_cont["exchangeInformation"],
                "Ocurrió un error al procesar el mensaje",
                session_manager.DynamicInformation.ES_UNDEFINED,
            ),
            500,
            {"Content-Type": "application/json"},
        )
        return response


@app.route("/v35/<d_payload>/openSession", methods=["POST"])
def open_session_v35(d_payload):
    """Opening session of session_manager"""
    try:
        datex_payload = request.data
        msg_cont = json.loads(datex_payload)
        is_valid, return_message, json_message = process_message(
            d_payload, msg_cont, settings.DATEX_MESSAGE_CONTAINER, "3.5"
        )
        # logging.info(return_message)
        # logging.info(json_message)
        if is_valid:
            agency, msg = session_manager.open_session(msg_cont)
            response = msg, 200, {"Content-Type": "application/json"}
            logging.info(response)
        else:
            logging.info("Else from main")
            msg = session_manager.failed_process_status(
                msg_cont["exchangeInformation"],
                "La estructura del mensaje Datex no es correcto ",
                session_manager.DynamicInformation.ES_OFFLINE,
            )
            response = msg, 400, {"Content-Type": "application/json"}
        return response
    except Exception as exp:
        logging.error(exp)
        msg = str(exp)
        return msg, 500, {"Content-Type": "application/json"}


@app.route("/<d_payload>/openSession", methods=["POST"])
def open_session(d_payload):
    """Opening session of session_manager"""
    try:
        logging.info(request.data)
        datex_payload = request.data
        msg_cont = json.loads(datex_payload)
        is_valid, return_message, json_message = process_message(
            d_payload, msg_cont, settings.DATEX_MESSAGE_CONTAINER, "3.1"
        )
        logging.info(return_message)
        logging.info(json_message)
        if is_valid:
            agency, msg = session_manager.open_session(msg_cont)
            response = msg, 200, {"Content-Type": "application/json"}
            logging.info(response)
        else:
            logging.info("Else from main")
            msg = session_manager.failed_process_status(
                msg_cont["exchangeInformation"],
                "La estructura del mensaje Datex no es correcto ",
                session_manager.DynamicInformation.ES_OFFLINE,
            )
            response = msg, 400, {"Content-Type": "application/json"}
        return response
    except Exception as exp:
        logging.error(exp)
        msg = str(exp)
        return msg, 500, {"Content-Type": "application/json"}


@app.route("/v35/<d_payload>/closeSession", methods=["POST"])
def close_session_v35(d_payload):
    try:
        datex_payload = request.data
        msg_cont = json.loads(datex_payload)
        is_valid, return_message, json_message = process_message(
            d_payload, msg_cont, settings.DATEX_MESSAGE_CONTAINER, "3.5"
        )
        if is_valid:
            agency, msg = session_manager.close_session(msg_cont)
            logging.info("Closing session of %d", agency)
            response = msg, 200, {"Content-Type": "application/json"}
        else:
            response = (
                session_manager.failed_process_status(
                    msg_cont["exchangeInformation"],
                    "La estructura del mensaje Datex no es correcto ",
                    session_manager.DynamicInformation.ES_OFFLINE,
                ),
                400,
                {"Content-Type": "application/json"},
            )
        return response
    except Exception as exp:
        logging.error(exp)
        msg = str(exp)
        return msg, 500, {"Content-Type": "application/json"}


@app.route("/<d_payload>/closeSession", methods=["POST"])
def close_session(d_payload):
    """Closing session of session_manager"""
    try:
        datex_payload = request.data
        msg_cont = json.loads(datex_payload)
        is_valid, return_message, json_message = process_message(
            d_payload, msg_cont, settings.DATEX_MESSAGE_CONTAINER, "3.1"
        )
        logging.info(return_message)
        logging.info(json_message)
        if is_valid:
            agency, msg = session_manager.close_session(msg_cont)
            logging.info("Closing session of %d", agency)
            response = msg, 200, {"Content-Type": "application/json"}
        else:
            response = (
                session_manager.failed_process_status(
                    msg_cont["exchangeInformation"],
                    "La estructura del mensaje Datex no es correcto ",
                    session_manager.DynamicInformation.ES_OFFLINE,
                ),
                400,
                {"Content-Type": "application/json"},
            )
        return response
    except Exception as exp:
        logging.error(exp)
        msg = str(exp)
        return msg, 500, {"Content-Type": "application/json"}


if __name__ == "__main__":
    logging.info("Inicio del servido")
    app.run(debug=True, host="0.0.0.0", port=8000)
