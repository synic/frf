import unittest
import os

from frf._conf import Conf


class TestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.conf = Conf(
            'frf.tests.fakeproject.settings', os.path.dirname(__file__))

    def test_access_setting_via_dict(self):
        self.assertEqual(
            self.conf['TIMEZONE'], 'US/Mountain')

    def test_access_via_property(self):
        self.assertEqual(
            self.conf.TIMEZONE, 'US/Mountain')

    def test_set_via_property(self):
        self.conf.WOOT = True

        self.assertTrue(self.conf['WOOT'])

    def test_fail_file_not_found(self):
        with self.assertRaises(ImportError):
            Conf('thissettingsfile.should.not.exist')

    def test_get_path_of_file(self):
        self.assertIn(
            'frf/tests/test_conf.py', self.conf.pathof('test_conf.py'))
