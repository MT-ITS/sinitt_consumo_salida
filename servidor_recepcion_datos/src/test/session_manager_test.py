import sys
import json
import unittest
from unittest import mock

sys.path.insert(0, "../src")
from session_manager.session_manager import *
from datetime import datetime
from session_manager import session_manager


class session_manager_test(unittest.TestCase):
    def test_get_current_date(self):
        result = datetime.strptime(get_current_date(), "%Y-%m-%dT%H:%M:%S.%f").strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        test = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self.assertEqual(result, test)

    def test_status_reason(self):
        result = status_reason("situtation", "english")
        test = [{"lang": "english", "value": "situtation"}]
        self.assertEqual(result, test)

    def test_succes_process_status(self):
        exchange_info = json.load(
            open(
                "test/SampleMessageExchange/Sample_Client_responses/openSession_OKresponse.json"
            )
        )["exchangeInformation"]
        succes_reason = "test"
        result = json.loads(succes_process_status(exchange_info, succes_reason))
        session_id = exchange_info["DynamicInformation"]["sessionInformation"][
            "sessionID"
        ]
        dyn_object = DynamicInformation("online", session_id, "ack")
        dynamic_information = json.loads(dyn_object.to_json())
        dynamic_information["returnInformation"]["returnStatusReason"] = status_reason(
            succes_reason, "es"
        )

        test_2 = (
            result["exchangeInformation"]["ExchangeContext"]["codedExchangeProtocol"]
            == exchange_info["ExchangeContext"]["codedExchangeProtocol"]
        )
        test_3 = (
            result["exchangeInformation"]["DynamicInformation"][
                "messageGenerationTimestamp"
            ]
            == dynamic_information["messageGenerationTimestamp"],
        )
        self.assertIn("exchangeInformation", result)
        self.assertTrue(test_2)
        self.assertTrue(test_3)

    def test_failed_process_status_if(self):
        exchange_info = json.load(
            open(
                "test/SampleMessageExchange/Sample_Client_responses/openSession_OKresponse.json"
            )
        )["exchangeInformation"]
        status = "online"
        failed_process_reason = "test"
        session_id = exchange_info["DynamicInformation"]["sessionInformation"][
            "sessionID"
        ]

        dyn_object_1 = DynamicInformation("online", session_id, "fail")
        dynamic_information_1 = json.loads(dyn_object_1.to_json())
        dynamic_information_1["returnInformation"][
            "returnStatusReason"
        ] = status_reason(failed_process_reason, "es")

        result_1 = json.loads(
            failed_process_status(exchange_info, failed_process_reason, status)
        )

        self.assertIn("exchangeInformation", result_1)

        test_2 = (
            result_1["exchangeInformation"]["ExchangeContext"]["codedExchangeProtocol"]
            == exchange_info["ExchangeContext"]["codedExchangeProtocol"]
        )

        test_3 = (
            result_1["exchangeInformation"]["DynamicInformation"][
                "messageGenerationTimestamp"
            ]
            == dynamic_information_1["messageGenerationTimestamp"],
        )

        self.assertTrue(test_2)
        self.assertTrue(test_3)

    def test_failed_process_status_else(self):
        exchange_info_dynamic_inf = json.load(
            open(
                "test/SampleMessageExchange/Sample_Client_responses/openSession_OKresponse.json"
            )
        )["exchangeInformation"]
        del exchange_info_dynamic_inf["DynamicInformation"]["sessionInformation"]
        status = "online"
        failed_process_reason = "test"

        dyn_object_2 = DynamicInformation("online", "fail")
        dynamic_information_2 = json.loads(dyn_object_2.to_json())
        dynamic_information_2["returnInformation"][
            "returnStatusReason"
        ] = status_reason(failed_process_reason, "es")

        result_2 = json.loads(
            failed_process_status(
                exchange_info_dynamic_inf, failed_process_reason, status
            )
        )

        self.assertIn("exchangeInformation", result_2)

        test_4 = (
            result_2["exchangeInformation"]["ExchangeContext"]["codedExchangeProtocol"]
            == exchange_info_dynamic_inf["ExchangeContext"]["codedExchangeProtocol"]
        )

        test_5 = (
            result_2["exchangeInformation"]["DynamicInformation"][
                "messageGenerationTimestamp"
            ]
            == dynamic_information_2["messageGenerationTimestamp"],
        )
        self.assertTrue(test_4)
        self.assertTrue(test_5)

    def test_not_active_session(self):
        exchange_info = json.load(
            open(
                "test/SampleMessageExchange/Sample_Client_responses/closeSession_OKresponse.json"
            )
        )["exchangeInformation"]
        result = json.loads(not_active_session(exchange_info))

        dyn_object = DynamicInformation(DynamicInformation.ES_OFFLINE, None, "fail")
        reason = status_reason("No existe una sesión activa", "es")

        exchange_info["DynamicInformation"] = json.loads(dyn_object.to_json())
        exchange_info["DynamicInformation"].pop("sessionInformation", None)
        exchange_info["DynamicInformation"]["returnInformation"][
            "returnStatusReason"
        ] = reason

        self.assertIn("exchangeInformation", result)
        self.assertEqual(
            result["exchangeInformation"]["DynamicInformation"]["returnInformation"][
                "returnStatusReason"
            ],
            exchange_info["DynamicInformation"]["returnInformation"][
                "returnStatusReason"
            ],
        )
        self.assertEqual(
            result["exchangeInformation"]["DynamicInformation"]["returnInformation"][
                "returnStatusReason"
            ],
            exchange_info["DynamicInformation"]["returnInformation"][
                "returnStatusReason"
            ],
        )

    def test_check_active(self):
        exchange_info = json.load(
            open(
                "test/SampleMessageExchange/Sample_Client_responses/openSession_OKresponse.json"
            )
        )["exchangeInformation"]
        active = check_active(exchange_info)
        self.assertEqual(active, False)

    def test_keep_alive(self):
        exchange_info = json.load(
            open(
                "test/SampleMessageExchange/Sample_Client_responses/openSession_OKresponse.json"
            )
        )
        works, result = keep_alive(exchange_info)
        result = json.loads(result)
        test1 = False
        test2 = json.loads(not_active_session(exchange_info["exchangeInformation"]))

        self.assertEqual(works, test1)
        self.assertEqual(
            result["exchangeInformation"]["ExchangeContext"]["Subscription"],
            test2["exchangeInformation"]["ExchangeContext"]["Subscription"],
        )

    def test_keep_alive_wrong(self):
        exchange_info = json.load(open("test/test_files/empty_file.json"))
        works, result = keep_alive(exchange_info)

        result = json.loads(result)
        test1 = False
        test2 = {
            "exchangeInformation": {
                "ExchangeContext": {},
                "DynamicInformation": {
                    "exchangeStatus": "offline",
                    "messageGenerationTimestamp": "2022-06-06T12:36:45.725710",
                    "returnInformation": {
                        "returnStatus": "fail",
                        "returnStatusReason": [
                            {"lang": "es", "value": "No existe una sesión activa"}
                        ],
                    },
                },
            }
        }
        del result["exchangeInformation"]["DynamicInformation"][
            "messageGenerationTimestamp"
        ]
        del test2["exchangeInformation"]["DynamicInformation"][
            "messageGenerationTimestamp"
        ]
        self.assertEqual(works, test1)
        self.assertEqual(
            result,
            test2,
        )

    def test_return_agency_if(self):
        exchange_info = json.load(
            open("test/test_files/opensession_ok_response_custom1.json")
        )
        result = return_agency(exchange_info)
        name = "test1"

        self.assertEqual(result, name)

    def test_return_agency_elif(self):
        exchange_info = json.load(
            open(
                "test/SampleMessageExchange/Sample_Client_responses/openSession_OKresponse.json"
            )
        )
        result = return_agency(exchange_info)
        test = "SINNIT"

        self.assertEqual(result, test)

    def test_return_agency_else(self):
        exchange_info = json.load(
            open("test/test_files/opensession_ok_response_custom2.json")
        )
        result = return_agency(exchange_info)
        name = "No Agency"

        self.assertEqual(result, name)

    def test_return_agency_wrong(self):
        exchange_info = json.load(open("test/test_files/empty_file2.json"))
        result = return_agency(exchange_info)
        name = "Agency error"

        self.assertEqual(result, name)

    @mock.patch("session_manager.session_manager.open_session")
    def test_open_session(self, mock_openSession):
        exchange_info = json.load(
            open("test/test_files/opensession_ok_response_custom1.json")
        )
        # open_session(exchange_info)
        mock_openSession(exchange_info)
        mock_openSession.assert_called_once()

    @mock.patch("session_manager.session_manager.open_session")
    def test_close_session(self, mock_closeSession):
        exchange_info = json.load(
            open("test/SampleMessageExchange/Sample_Requests_Body/closeSession_OK.json")
        )
        mock_closeSession(exchange_info)
        mock_closeSession.assert_called_once()

    @mock.patch("session_manager.session_manager.renew_session")
    def test_renew_session(self, mock_renew_session):
        mock_renew_session()
        mock_renew_session.assert_called_once()

    def test_dynamic_information_class(self):
        dynamic_information_class_instance = DynamicInformation()
        json1 = dynamic_information_class_instance.to_json()
        session_information_instance = (
            dynamic_information_class_instance.sessionInformation("test1")
        )
        json2 = session_information_instance.to_json()
        return_information_instance = (
            dynamic_information_class_instance.returnInformation("test1")
        )
        json3 = return_information_instance.to_json()
        self.assertEqual(
            dynamic_information_class_instance.ES_CLOSING_SESSION, "closingSession"
        )
        self.assertEqual(session_information_instance.sessionID, "test1")
        self.assertEqual(return_information_instance.returnStatus, "test1")

    def test_exchange_context_class(self):
        exchange_context_instance = ExchangeContext()
        json1 = exchange_context_instance.to_json()
        supplier_instance = exchange_context_instance.supplierOrCisRequester("test1")
        json2 = supplier_instance.to_json()

        self.assertEqual(json1, "{}")
        self.assertIn("name", json2)

    def test_exchange_context_class_2(self):
        exchange_context_instance = ExchangeContext()
        json1 = exchange_context_instance.to_json()
        supplier_instance = exchange_context_instance.supplierOrCisRequester(
            "test1", "test2"
        )
        json2 = supplier_instance.to_json()

        self.assertEqual(json1, "{}")
        self.assertIn("internationalIdentifier", json2)

    def test_exchange_context_class_3(self):
        exchange_context_instance = ExchangeContext("test1", "test2", "test3", "test4")
        json1 = exchange_context_instance.to_json()

        self.assertIn("internationalIdentifier", json1)

    def test_exchange_context_class_4(self):
        exchange_context_instance = ExchangeContext("test1", "test2", "test3")
        json1 = exchange_context_instance.to_json()

        self.assertIn("codedExchangeProtocol", json1)

    def test_exchange_information(self):
        exchange_context_instance = ExchangeContext()
        dynamic_information_class_instance = DynamicInformation()
        exchange_information_instance = exchangeInformation(
            exchange_context_instance, dynamic_information_class_instance
        )
        json = exchange_information_instance.to_json()
        include_key = exchange_information_instance.include_key(
            exchange_context_instance
        )
        self.assertEqual(exchange_information_instance._modelVersion, "3")
        self.assertIn("exchangeInformation", json)
