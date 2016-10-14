import unittest
import inspect

from frf.utils import importing


class TestCase(unittest.TestCase):
    def test_import_class(self):
        cls = importing.import_class(
            'frf.tests.test_utils.dummy_class.DummyClass')

        self.assertTrue(inspect.isclass(cls))
        self.assertEqual('stuff', cls().woot())

    def test_fail_import_missing_import(self):
        with self.assertRaises(ImportError):
            importing.import_class('thisshould.not.import.12112')

    def test_fail_import_not_a_class(self):
        with self.assertRaises(ImportError) as context:
            importing.import_class('frf.tests.test_utils.test_importing')

        self.assertIn('does not refer to a class', str(context.exception))
