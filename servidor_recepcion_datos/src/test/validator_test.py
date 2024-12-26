import os
import json
import unittest
import sys

print("hola")
print(sys.executable)
print("\n".join(sys.path))
print("hola")

sys.path.append("..")
from src.validator.validator import *


class validator_test(unittest.TestCase):
    def test_get_schema(self):
        path = "test/test_files/ejemplo_situaciones.json"
        result = get_schema(path)
        test = json.load(open(path))
        self.assertEqual(result, test)

    def test_validate_json_ok(self):
        path = "test/SampleMessageExchange/Sample_Client_responses/openSession_OKresponse.json"
        test_file = json.load(open(path))
        schema_dir = "test/test_files/validator/Datex_schemas"
        message_type = "D2MessageContainer"
        schema = get_schema(schema_dir + "/DATEXII_3_" + message_type + ".json")
        result_1, result_2 = validate_json(test_file, schema)
        test_1, test_2 = True, {
            "result": "Given JSON data is Valid",
        }
        self.assertEqual(result_1, test_1)
        self.assertEqual(result_2["result"], test_2["result"])

    def test_validate_json_wrong(self):
        test_file = {}
        schema_dir = "test/test_files/validator/Datex_schemas"
        message_type = "D2MessageContainer"
        schema = get_schema(schema_dir + "/DATEXII_3_" + message_type + ".json")
        result_1, result_2 = validate_json(test_file, schema)
        test_1, test_2 = False, {
            "error_description": "any error",
            "result": "Given JSON data is InValid",
        }
        self.assertEqual(result_1, test_1)
        self.assertEqual(result_2["result"], test_2["result"])

    def test_process_message_if(self):
        path = "test/test_files/ejemplo_situaciones.json"
        test_file = json.load(open(path))
        d_payload = "situationPublication"
        message_type = "D2MessageContainer"
        test_file["payload"] = d_payload
        result_1, result_2, result_3 = process_message(
            d_payload, test_file, message_type
        )
        test_1, test_2, test_3 = (
            False,
            {"error_description": "any error", "result": "Given JSON data is InValid"},
            json.dumps(test_file).encode("utf-8"),
        )
        self.assertEqual(result_1, test_1)
        self.assertEqual(result_2["result"], test_2["result"])
        self.assertEqual(result_3, test_3)

    def test_process_message_else(self):
        path = "test/test_files/ejemplo_situaciones.json"
        test_file = json.load(open(path))
        d_payload = "situationPublication"
        message_type = "D2MessageContainer"
        result_1, result_2, result_3 = process_message(
            d_payload, test_file, message_type
        )
        test_1, test_2, test_3 = (
            False,
            {"error_description": "any error", "result": "Given JSON data is InValid"},
            json.dumps(test_file).encode("utf-8"),
        )
        self.assertEqual(result_1, test_1)
        self.assertEqual(result_2["result"], test_2["result"])
        self.assertEqual(result_3, test_3)
