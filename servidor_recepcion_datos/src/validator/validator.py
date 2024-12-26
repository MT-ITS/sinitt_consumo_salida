"""Used Modules."""
import json
import os
import logging
import jsonschema
from jsonschema import validate, RefResolver

schema_dir_v3_1 = os.path.abspath('validator/Datex_schemas/v3.1/')
schema_dir_v3_5 = os.path.abspath('validator/Datex_schemas/v3.5/')


def process_message(payload_type, json_message, message_type, version="3.1"):
    """Processing of the json message."""
    if version == "3.1":
        logging.info(schema_dir_v3_1)
        schema = get_schema(schema_dir_v3_1 + "/DATEXII_3_" + message_type + ".json")

        if 'payload' in json_message:
            is_valid, msg = validate_json(json_message, schema_dir_v3_1, schema)
            str_json_message = json.dumps(json_message)
        else:
            is_valid = False
            is_valid, msg = validate_json(json_message, schema_dir_v3_1, schema)
            str_json_message = json.dumps(json_message)
        return is_valid, msg, str_json_message.encode('utf-8')
    elif version == "3.5":
        """Processing of the json message."""
        logging.info(">>>>>>>> src/validator/validator.py, en funcion process_message: schema_dir =:")
        logging.info(schema_dir_v3_5)
        schema = get_schema(schema_dir_v3_5+"/DATEXII_3_"+message_type+".json")

        if 'payload' in json_message:
            is_valid, msg = validate_json(json_message,schema_dir_v3_5, schema)
            str_json_message = json.dumps(json_message)
        else:
            is_valid = False
            is_valid, msg = validate_json(json_message, schema_dir_v3_5, schema)
            str_json_message = json.dumps(json_message)
        return is_valid,msg, str_json_message.encode('utf-8')
    else:
        logging.info(">>>>>>>> incorrect version given" + version)
        raise ValueError("incorrect version given - version:" + version)


def get_schema(schema):
    """This function loads the given schema available."""
    logging.info(">>>>>>>> src/validator/validator.py ,en funcion get_schema: el valor de parametro schema =")
    logging.info(schema)

    with open(schema) as file:
        schema = json.load(file)

    logging.info(">>>>>>>>>>>>> schema se ha calculado mediante: schema = json.load(file)")
    logging.info("schema = " + str(schema))

    return schema


def validate_json(json_data, schema_dir, schema):
    """validate if the json information has correct format."""
    schema_path = 'file:///{0}/'.format(schema_dir).replace("\\", "/")
    # logging.info('Schema directory:'+schema_path)
    resolver = RefResolver(schema_path, schema)
    # """REF: https://json-schema.org/ """
    # Describe what kind of json you expect.
    try:
        validate(instance=json_data, schema=schema, resolver=resolver)
    except jsonschema.exceptions.ValidationError as err:
        logging.info(err)
        err_json = {'error_description': str(err), 'result': "Given JSON data is InValid"}
        # TODO log result # pylint: disable=fixme
        return False, err_json
    message = {"result": "Given JSON data is Valid"}
    return True, message
