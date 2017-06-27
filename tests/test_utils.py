import pytest
from autoscaler import utils


# from https://goodcode.io/articles/python-dict-object/
class objdict(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)


class TestUtil(object):

    @pytest.mark.parametrize("test_input,expected", [
        ('0 B', 0),
        ('1 K', 1024),
        ('1 M', 1048576),
        ('1 Gi', 1073741824),
        ('1 tera', 1099511627776),
        ('0.5kilo', 512),
        ('0.1  byte', 0),
        ('1 k', 1024),
        ('12 foo', ValueError)
    ])
    def test_human2bytes(self, test_input, expected):
        if isinstance(expected, int):
            assert utils.human2bytes(test_input) == expected
        else:
            with pytest.raises(expected):
                utils.human2bytes(test_input)

    @pytest.mark.parametrize("test_input,expected", [
        ('0', 0),
        ('12345', 12345),
        ('0 B', 0),
        ('1 K', 1024),
        ('1 M', 1048576),
        ('1 Gi', 1073741824),
        ('1 tera', 1099511627776),
        ('0.5kilo', 512),
        ('0.1  byte', 0),
        ('1 k', 1024),
        ('12 foo', ValueError),
        ('345.324235543', ValueError)
    ])
    def test_convert_size(self, test_input, expected):
        if isinstance(expected, int):
            assert utils.convert_size(test_input) == expected
        else:
            with pytest.raises(expected):
                utils.convert_size(test_input)

    @pytest.mark.parametrize("list1,list2,expected", [
        ([1, 2, 3], [4, 5, 6], False),
        ([1, 2, 3, 8, 9, 23, 345, 234, 898, 2343], [4, 5, 6], False),
        ([1, 2, 3], [4, 3, 6], True),
        ([1, 2, 3, 34, 5465, 23, 435, 97, 34], [4, 3, 6], True),
        ([1, 2, 3, 34, 5465, 23, 435, 97, 34], [4, 3, 6, 97, 2, 3], True),
        (None, [4, 6, 6], False),
        (None, None, False)
    ])
    def test_check_list_intersection(self, list1, list2, expected):
        assert utils.check_list_intersection(list1, list2) == expected and \
               utils.check_list_intersection(list2, list1) == expected

    def test_user_confirm(self, capsys):
        input_return = ''

        def input_test(prompt):
            print(prompt)
            return input_return

        utils.input = input_test
        assert utils.user_confirm(prompt='Create Directory?', default_response=True)
        out, err = capsys.readouterr()
        assert out == 'Create Directory? [Y/n] \n'

        assert not utils.user_confirm(prompt='Create Directory?', default_response=False)
        out, err = capsys.readouterr()
        assert out == 'Create Directory? [y/N] \n'

        assert utils.user_confirm(prompt='Hello World', default_response=True)
        out, err = capsys.readouterr()
        assert out == 'Hello World [Y/n] \n'

        input_return = 'y'
        assert utils.user_confirm(prompt='Create Directory?', default_response=False)

        input_return = 'Y'
        assert utils.user_confirm(prompt='Create Directory?', default_response=False)

        input_return = 'n'
        assert not utils.user_confirm(prompt='Create Directory?', default_response=False)

        input_return = 'N'
        assert not utils.user_confirm(prompt='Create Directory?', default_response=False)

    @pytest.mark.parametrize("node,expected", [
        (objdict(status=objdict(capacity=dict(memory='0'))), 0),
        (objdict(status=objdict(capacity=dict(memory='12345'))), 12345),
        (objdict(status=objdict(capacity=dict(memory='0 B'))), 0),
        (objdict(status=objdict(capacity=dict(memory='1 K'))), 1024),
        (objdict(status=objdict(capacity=dict(memory='1 M'))), 1048576),
        (objdict(status=objdict(capacity=dict(memory='1 Gi'))), 1073741824),
        (objdict(status=objdict(capacity=dict(memory='1 tera'))), 1099511627776),
        (objdict(status=objdict(capacity=dict(memory='0.5kilo'))), 512),
        (objdict(status=objdict(capacity=dict(memory='0.1  byte'))), 0),
        (objdict(status=objdict(capacity=dict(memory='1 k'))), 1024),
        (objdict(status=objdict(capacity=dict(memory='12 foo'))), ValueError),
        (objdict(status=objdict(capacity=dict(memory='345.324235543'))), ValueError),
        (objdict(status=objdict(capacity=dict(memory2='1 k'))), KeyError),
        (objdict(status=objdict(capacity2=dict(memory='1 k'))), AttributeError),
        (objdict(status2=objdict(capacity=dict(memory='1 k'))), AttributeError),
    ])
    def test_get_node_memory_capacity(self, node, expected):
        if isinstance(expected, int):
            assert utils.get_node_memory_capacity(node) == expected
        else:
            with pytest.raises(expected):
                utils.get_node_memory_capacity(node)
