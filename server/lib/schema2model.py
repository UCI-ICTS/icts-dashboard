"""
Json Schema to Django Model
"""
import json
import argparse
import logging
import os


def determine_model_name(model_id=None, filename=None):
    """
    Get the model name
    :param model_id: str, model id
    :param filename: str, filename
    :return: str, model name
    """
    model_name = ''
    if model_id:
        try:
            model_name = model_id.split('/')[-1].replace('.json', '')
        except Exception as e:
            logging.exception("Unhandled exception {}".format(e))

    if not model_name and filename:
        filename = filename.strip(os.sep)
        model_name = filename.split(os.sep)[-1]
        model_name = model_name.split('.')[0]

    return model_name.capitalize() or 'UnknownModel'


def get_required_string(key_name, required_fields, field_type='string', is_pk_field=False):
    """
    Gets the required portion of model field
    :param key_name:
    :param required_fields:
    :return: str, required model string
    """
    if is_pk_field:
        return 'primary_key=True'

    if field_type in ('number', 'array', 'object'):
        if key_name in required_fields:
            return 'null=False'
        return 'null=True'
    else:  # string, boolean
        if key_name in required_fields:
            return 'null=False, blank=False'
        return 'null=True, blank=True'


def parse_model():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()
    filename = args.filename

    with open(filename) as f:
        json_model = json.load(f)
    import pdb; pdb.set_trace()
    # Make sure not list, but object
    if json_model['type'] != 'object':

        print("Model type has to be object to convert to model, got {}".format(json_model['type']))

    if 'oneOf' in json_model:
        print("Optional required fields detected: {}".format(json_model['oneOf']))

    # Default model string
    model_str = "\nfrom djongo import models\nfrom djongo.models import json\n\n"

    model_name = determine_model_name(json_model.get('id'), args.filename)
    model_str += "class {}(models.Model):\n".format(model_name)
    model_str += '    """Generated model from json schema"""\n'
    print("Model name is {}".format(model_name))

    if 'title' in json_model:
        print("Title of model is {}".format(json_model['title']))

    if 'description' in json_model:
        print("Description of model is {}".format(json_model['description']))

    required_fields = []
    if 'required' in json_model:
        required_fields = json_model['required']

    for key_name, key_attributes in json_model['properties'].items():
        if key_name.endswith('_id') and key_name != '_id':
            print("WARNING: Possible ForeignKey {}".format(key_name))

        # if key_attributes['type'] == 'array':
        #     print("ERROR: Unsupported type array, skipping for field {}".format(key_name))

        if key_attributes['type'] == 'null':
            print("ERROR: Unsupported type null, skipping for field {}".format(key_name))

        # PK field
        is_pk_field = False
        if key_name in ['id', '_id']:
            is_pk_field = True

        # If required field
        required_str = get_required_string(key_name, required_fields, key_attributes['type'], is_pk_field)
        field_str = ''

        # String choice field, enum
        if key_attributes['type'] == 'string' and 'enum' in key_attributes:
            if not key_attributes['enum']:
                print("ERROR: Missing enum for enum choice field {}, skipping..".format(key_name))
                continue

            if len(key_attributes['enum']) == 1:
                print("WARNING: enum value with single choice for field {}, choice {}."
                      "".format(key_name, key_attributes['enum']))
                continue

            # Max length find
            max_length = 255
            for choice in key_attributes['enum']:
                if len(choice) > 255:
                    max_length = len(choice)

            choices = tuple(set(zip(key_attributes['enum'], key_attributes['enum'])))

            field_str = "    {} = models.CharField(choices={}, max_length={}, " \
                        "default='{}', {})\n" \
                        "".format(key_name, choices, max_length, key_attributes['enum'][0], required_str)

        # Date time field
        elif key_attributes['type'] == 'string' and key_attributes.get('format') == 'date-time':
            auto_now_add = False
            editable = True
            if key_name in ['created_on', 'modified_on']:
                auto_now_add = True
                editable = False

            field_str = "    {} = models.DateTimeField(auto_now_add={}, editable={}, {})\n" \
                        "".format(key_name, auto_now_add, editable, required_str)

        elif key_attributes['type'] == 'string':
            field_str = "    {} = models.TextField({})\n".format(key_name, required_str)

        elif key_attributes['type'] == 'number':
            field_str = "    {} = models.IntegerField({})\n".format(key_name, required_str)

        elif key_attributes['type'] == 'array':
            field_str = "    {} = json.JSONField(default=[], {})\n".format(key_name, required_str)

        elif key_attributes['type'] == 'object':
            field_str = "    {} = json.JSONField(default={{}}, {})\n".format(key_name, required_str)

        elif key_attributes['type'] == 'boolean':
            field_str = "    {} = models.BooleanField(default=False, {})\n".format(key_name, required_str)

        model_str += field_str

    model_str += "\n    class Meta:\n        db_table = '{}s'\n".format(model_name.lower())

    print(model_str)


if __name__ == "__main__":
    parse_model()
