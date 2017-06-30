import pytest
import json
from collections import namedtuple


# from https://goodcode.io/articles/python-dict-object/
class objdict(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)


def check_expected(f, test_inputs, expected_class, expected):
    if isinstance(expected, expected_class):
        assert f(*test_inputs) == expected
    else:
        with pytest.raises(expected):
            f(*test_inputs)


# from: https://stackoverflow.com/questions/6578986/how-to-convert-json-data-into-a-python-object
def _json_object_hook(d):
    return namedtuple('X', d.keys(), rename=True)(*d.values())


def json_to_object(file_name):
    json_object = None
    with open(file_name, 'r') as json_file:
        json_object = json.load(json_file, object_hook=_json_object_hook)
    return json_object


def log_output(file_name, output):
    # logs a str output to a file
    with open('tests/logs/{}.txt'.format(file_name), 'a+') as file:
        file.write(output + "\n\n")
