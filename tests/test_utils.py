import pytest
from autoscaler import utils


class TestUtil(object):

    def test_human2bytes(self):
        assert utils.human2bytes('0 B') == 0
        assert utils.human2bytes('1 K') == 1024
        assert utils.human2bytes('1 M') == 1048576
        assert utils.human2bytes('1 Gi') == 1073741824
        assert utils.human2bytes('1 tera') == 1099511627776
        assert utils.human2bytes('0.5kilo') == 512
        assert utils.human2bytes('0.1  byte') == 0
        assert utils.human2bytes('1 k') == 1024

        with pytest.raises(ValueError):
            utils.human2bytes('12 foo')

    def test_convert_size(self):
        assert utils.convert_size("12345") == 12345
        assert utils.convert_size("0") == 0
        assert utils.convert_size('0 B') == 0
        assert utils.convert_size('1 K') == 1024
        assert utils.convert_size('1 M') == 1048576
        assert utils.convert_size('1 Gi') == 1073741824
        assert utils.convert_size('1 tera') == 1099511627776
        assert utils.convert_size('0.5kilo') == 512
        assert utils.convert_size('0.1  byte') == 0
        assert utils.convert_size('1 k') == 1024

        with pytest.raises(ValueError):
            utils.convert_size('12 foo')

        with pytest.raises(ValueError):
            utils.convert_size("345.324235543")

    def test_check_list_intersection(self):
        list1 = [1, 2, 3]
        list2 = [4, 5, 6]
        assert not utils.check_list_intersection(list1, list2)
        assert not utils.check_list_intersection(list2, list1)
        list1 = [1, 2, 3, 8, 9, 23, 345, 234, 898, 2343]
        list2 = [4, 5, 6]
        assert not utils.check_list_intersection(list1, list2)
        assert not utils.check_list_intersection(list2, list1)
        list1 = [1, 2, 3]
        list2 = [4, 3, 6]
        assert utils.check_list_intersection(list1, list2)
        assert utils.check_list_intersection(list2, list1)
        list1 = [1, 2, 3, 34, 5465, 23, 435, 97, 34]
        list2 = [4, 3, 6]
        assert utils.check_list_intersection(list1, list2)
        assert utils.check_list_intersection(list2, list1)
        list1 = [1, 2, 3, 34, 5465, 23, 435, 97, 34]
        list2 = [4, 3, 6, 97, 2, 3]
        assert utils.check_list_intersection(list1, list2)
        assert utils.check_list_intersection(list2, list1)
        list1 = None
        list2 = [4, 3, 6]
        assert not utils.check_list_intersection(list1, list2)
        assert not utils.check_list_intersection(list2, list1)
        list1 = None
        list2 = None
        assert not utils.check_list_intersection(list1, list2)
        assert not utils.check_list_intersection(list2, list1)

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
