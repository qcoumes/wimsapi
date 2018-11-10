import unittest

from wimsapi.api import WimsAPI

WIMS_URL = "http://localhost:7777/wims/wims.cgi"


class WimsAPITestCase(unittest.TestCase):

    def test_init_and_properties(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        self.assertEqual(api.url, WIMS_URL)
        self.assertEqual(api.ident, "myself")
        self.assertEqual(api.passwd, "toto")

    def test_check_ident(self):
        self.assertTrue(WimsAPI(WIMS_URL, "myself", "toto").checkident()[0])
        self.assertFalse(WimsAPI(WIMS_URL, "wrong", "wrong").checkident()[0])