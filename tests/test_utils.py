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
