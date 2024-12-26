import os
import json
import unittest
import sys
import flask_unittest
import asyncio

sys.path.insert(0, "../src")
from main import *
from main import app
from unittest import mock


def create_app(app):
    return app


class Main_test_unittest(unittest.TestCase):
    @mock.patch("main.separar_json")
    def test_separar_json(self, mock_separar_json):
        mock_separar_json({})
        mock_separar_json.assert_called_once()


class Main_test_flask_test(flask_unittest.ClientTestCase):

    app = create_app(app)

    def test_enrich_json(self, client):
        json_original = json.load(open("test/test_files/ejemplo_situaciones.json"))
        d_payload = "situationPublication"
        agencia = "12"

        enriched_json = enrich_json(json_original, agencia, d_payload)

        self.assertIn("filterAttributes", enriched_json)
        self.assertIn("agency", enriched_json["filterAttributes"])
        self.assertEqual("12", enriched_json["filterAttributes"]["agency"])
        self.assertIn("datexMessageType", enriched_json["filterAttributes"])
        self.assertEqual(
            "situationPublication",
            enriched_json["filterAttributes"]["datexMessageType"],
        )
        self.assertIn("datexPublicationData", enriched_json)
        self.assertEqual(json_original, enriched_json["datexPublicationData"])

    def test_well_formed(self, client):
        payload = json.load(open("test/test_files/ejemplo_situaciones.json"))
        d_payload = "situationPublication"

        is_valid, return_message, json_message = well_formed_container(
            payload, d_payload
        )

        self.assertEqual(is_valid, False)
        self.assertEqual(return_message["result"], "Given JSON data is InValid")
        self.assertEqual(json.loads(json_message), payload)

    def test_open_session(self, client):

        exchange_info = json.load(
            open("test/SampleMessageExchange/Sample_Requests_Body/openSession_ex.json")
        )
        lResp = client.post("/<d_payload>/openSession", data=exchange_info)
        print(lResp.status_code)
        self.assertEqual(lResp.status_code, 500)

    def test_close_session(self, client):

        exchange_info = json.load(
            open("test/SampleMessageExchange/Sample_Requests_Body/openSession_ex.json")
        )
        lResp = client.post("/<d_payload>/closeSession", data=exchange_info)
        print(lResp.status_code)
        self.assertEqual(lResp.status_code, 500)

    def test_put_data(self, client):

        d_payload = "situationPublication"
        lResp = client.post("/<d_payload>/putData", data=d_payload)
        self.assertEqual(lResp.status_code, 500)

    def test_put_snapshot_data(self, client):

        d_payload = "situationPublication"
        lResp = client.post("/<d_payload>/putSnapShotData", data=d_payload)
        self.assertEqual(lResp.status_code, 500)

    def test_keep_alive(self, client):

        d_payload = "situationPublication"
        lResp = client.post("/<d_payload>/keepAlive", data=d_payload)
        self.assertEqual(lResp.status_code, 500)


# Pass the flask app to suite
suite = flask_unittest.LiveTestSuite(create_app(app))
# Add the testcase
suite.addTest(unittest.makeSuite(Main_test_flask_test))
# Run the suite
unittest.TextTestRunner(verbosity=2).run(suite)
