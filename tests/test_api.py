import unittest

from wimsapi.api import WimsAPI

WIMS_URL = "http://www.localhost:7777/wims/"


class WimsAPITestCase(unittest.TestCase):

    def test_init_and_properties(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        self.assertEqual(api.url, WIMS_URL)
        self.assertEqual(api.ident, "myself")
        self.assertEqual(api.passwd, "toto")