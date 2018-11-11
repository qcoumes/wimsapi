import unittest

from wimsapi.api import WimsAPI


WIMS_URL = "http://localhost:7777/wims/wims.cgi"



class WimsAPITestCase(unittest.TestCase):
    """Getters are tested fist since other tests rely on them."""
    
    def test_00_init_and_properties(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        self.assertEqual(api.url, WIMS_URL)
        self.assertEqual(api.ident, "myself")
        self.assertEqual(api.passwd, "toto")
    
    
    def test_01_getclass(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getclass(9001, "myclass")
        self.assertTrue(status)
        self.assertEqual(response['description'], 'Aide au d veloppement de ressources.')
    
    def test_02_getuser(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getuser(9001, "myclass", "supervisor")
        self.assertTrue(status)
        self.assertEqual(response['firstname'], 'Sophie')


    # @unittest.skip("Response from WIMS server is not in JSON format.")
    def test_03_getsheet(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getsheet(9001, "myclass", 3)
        self.assertTrue(status)
        self.assertEqual(response['sheet_title'], "Syntaxe des exercices OEF à réponse prédéfinie")

    # @unittest.skip("Response from WIMS server is not in JSON format.")
    def test_04_getexo(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getexo(9001, "myclass", 3, 1)
        self.assertTrue(status)
        self.assertEqual(response['sheet_title'], "Syntaxe des exercices OEF à réponse prédéfinie")

    # @unittest.skip("Response from WIMS server is not in JSON format.")
    def test_05_getexam(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getexam(9001, "myclass", 1)
        self.assertTrue(status)
        self.assertEqual(response['sheet_title'], "Syntaxe des exercices OEF à réponse prédéfinie")
    
    
    def test_checkident(self):
        self.assertTrue(WimsAPI(WIMS_URL, "myself", "toto").checkident()[0])
        self.assertFalse(WimsAPI(WIMS_URL, "wrong", "wrong").checkident()[0])
