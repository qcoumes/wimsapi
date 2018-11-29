import unittest

from wimsapi.api import WimsAPI


WIMS_URL = "http://localhost:7777/wims/wims.cgi"

CSV = """login,password,name,lastname,firstname,email,regnum
desc,desc,desc,desc,desc,desc,desc
jdoe,password,Jhon Doe,Doe,Jhon,jhon@email.fr,1
qcoumes,password,Quentin Coumes,Coumes,Quentin,quentin@mail.fr,2"""



class WimsAPITestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Remove class potentially created by tests"""
        api = WimsAPI(WIMS_URL, "myself", "toto")
        api.delclass(999999, "myclass")
        api.delclass(999666, "myclass")
        api.delclass(999990, "myclass")
    
    
    def test_init_and_properties(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        self.assertEqual(api.url, WIMS_URL)
        self.assertEqual(api.ident, "myself")
        self.assertEqual(api.passwd, "toto")
    
    
    def test_0_addclass(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.addclass(
            999999,
            "myclass",
            {
                'description': "Test class",
                "institution": "Test institution",
                "supervisor" : "Test supervisor",
                "email"      : "Test@mail.com",
                "password"   : "password",
                "lang"       : "fr",
                "limit"      : 500
            },
            {
                "lastname" : "Doe",
                "firstname": "Jhon",
                "password" : "password"
            }
        )
        self.assertTrue(status)
        self.assertEqual(response['message'], "class 999999 correctly added")
    
    
    def test_addexam(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.addexam(999999, "myclass", {})
        self.assertTrue(status)
        self.assertEqual(response['message'], "exam #1 correctly added")
    
    
    def test_addexo(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.addexo(999999, "myclass", 1, r"\text{ a = \ma_matrice[1;] } ", True)
        self.assertTrue(status)
        self.assertEqual(response['message'], "exercice 1 successfully added")
    
    
    def test_addsheet(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.addsheet(999999, "myclass", {})
        self.assertTrue(status)
    
    
    def test_adduser(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.adduser(
            999999,
            "myclass",
            "jdoe",
            {
                "lastname" : "Doe",
                "firstname": "Jhon",
                "password" : "password"
            }
        )
        self.assertTrue(status)
        self.assertEqual(response['message'], "user jdoe correctly added")
    
    
    def test_authuser(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.authuser(999999, "myclass", "supervisor")
        self.assertTrue(status)
        self.assertTrue('wims_session' in response)
    
    
    def test_authuser_hash(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.authuser(999999, "myclass", "supervisor", "SHA1")
        self.assertTrue(status)
        self.assertTrue('wims_session' in response)
    
    
    def test_buildexos(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.buildexos(999999, "myclass")
        self.assertFalse(status)
        self.assertEqual(response['message'], "COMPILATION ERROR No statement defined.")
    
    
    def test_checkclass(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.checkclass(999999, "myclass")
        self.assertTrue(status)
        self.assertEqual(response['message'], "Class exists")
    
    
    def test_checkexam(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.checkexam(999999, "myclass", 1)
        self.assertTrue(status)
        self.assertEqual(response['message'], "exam 1 exists")
    
    
    def test_checkident(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.checkident()
        self.assertTrue(status)
        self.assertEqual(response['message'], "Connection accepted")
    
    
    def test_checksheet(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.checksheet(999999, "myclass", 1)
        self.assertTrue(status)
        self.assertEqual(response['message'], "sheet 1 exists")
    
    
    def test_checkuser(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.checkuser(999999, "myclass", "supervisor")
        self.assertTrue(status)
        self.assertEqual(response['message'], 'user supervisor exists')
    
    
    def test_cleanclass(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.cleanclass(999999, "myclass")
        self.assertTrue(status)
        self.assertEqual(response['message'], 'class 999999 correctly cleaned')
    
    
    @unittest.skip("Unstable on WIMS server.")
    def test_copyclass(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.copyclass(999999, "myclass")
        self.assertTrue(status)
        self.assertEqual(response['message'], 'class 999999 correctly copied as ')
    
    
    def test_delclass(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.addclass(
            999666,
            "myclass",
            {
                'description': "Test class",
                "institution": "Test institution",
                "supervisor" : "Test supervisor",
                "email"      : "Test@mail.com",
                "password"   : "password",
                "lang"       : "fr"
            },
            {
                "lastname" : "Doe",
                "firstname": "Jhon",
                "password" : "password"
            }
        )
        self.assertTrue(status)
        self.assertEqual(response['message'], "class 999666 correctly added")
        
        status, response = api.delclass(999666, "myclass")
        self.assertTrue(status)
        self.assertEqual(response['message'], "class 999666 correctly deleted")
    
    
    def test_delexam(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.addexam(999999, "myclass", {})
        self.assertTrue(status)
        self.assertEqual(response['message'], "exam #2 correctly added")
        
        status, response = api.delexam(999999, "myclass", 2)
        self.assertTrue(status)
        self.assertEqual(response['message'], "Exam #2 of class 999999 correctly deleted")
    
    
    def test_delexo(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.delexo(999999, "myclass", 1)
        self.assertFalse(status)
        self.assertEqual(response['message'], "1 NOT exists in this Class !")
    
    
    def test_delsheet(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.addsheet(999999, "myclass", {})
        self.assertTrue(status)
        
        status, response = api.delsheet(999999, "myclass", 2)
        self.assertTrue(status)
        self.assertEqual(response['message'], "sheet #2 of class 999999 correctly deleted")
    
    
    def test_deluser(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.adduser(
            999999,
            "myclass",
            "jdoe2",
            {
                "lastname" : "Doe",
                "firstname": "Jhon",
                "password" : "password"
            }
        )
        self.assertTrue(status)
        self.assertEqual(response['message'], "user jdoe2 correctly added")
        
        status, response = api.deluser(999999, "myclass", "jdoe2")
        self.assertTrue(status)
        self.assertEqual(response['message'], "User jdoe2 moved to trash.")
    
    
    def test_getclass(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getclass(9001, "myclass")
        self.assertTrue(status)
        self.assertEqual(response['description'], 'Aide au d veloppement de ressources.')
    
    
    def test_getclass_options(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getclass(9001, "myclass", ["password"])
        self.assertTrue(status)
        self.assertIn("password", response)
    
    
    def test_getclassesuser(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getclassesuser("myclass", "supervisor")
        self.assertTrue(status)
        self.assertEqual(response['classes_list'], [{'qclass': '999999'}])
    
    
    def test_getclassfile(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getclassfile(999999, "myclass", '.log')
        self.assertTrue(status)
        self.assertEqual(response[34:49], b"User jdoe added")
    
    
    @unittest.skip("WIMS' response json is invalid")
    def test_getclassmodif(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getclassmodif(999999, "myclass", '19700101')
        self.assertTrue(status)
        self.assertEqual(1, 2)
    
    
    @unittest.skip("Binary is invalid, html header present inside")
    def test_getclasstgz(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getclasstgz(999999, "myclass")
        self.assertTrue(status)
        self.assertEqual(response, b"User jdoe added")
    
    
    def test_getcsv(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getcsv(9001, "myclass", ["login", "password", "name", "email"])
        self.assertTrue(status)
        self.assertEqual(response,
                         b'login,password,lastname,firstname,email\n"#","Password","Family name",'
                         b'"First (given) name","email address"\n\n"quser","password","lastname",'
                         b'"firstname","mail@mail.com"\n"user","*Nv7lZCTkcYORw","User","user",'
                         b'""\n"anonymous","anonymous","Visiteur","Anonyme",""\n')
        
        
        def test_getexam(self):
            
            
            api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getexam(999999, "myclass", 1)
        self.assertTrue(status)
        self.assertEqual(response['exam_title'], "Examen #1")
    
    
    def test_getexamlog(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getexamlog(999999, "myclass", "supervisor", 1)
        self.assertFalse(status)
        self.assertEqual(response['message'],
                         "the user supervisor hasn't any exam log in this class.")
    
    
    def test_getexamscores(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getexamscores(999999, "myclass", 1)
        self.assertFalse(status)
        self.assertEqual(response['message'], "Exam #1 must be active")
    
    
    def test_getexo(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getexo(9001, "myclass", 3, 1)
        self.assertTrue(status)
        self.assertEqual(response['exo_title'], "Choice 1")
    
    
    def test_getexofile(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getexofile(9001, "myclass", 1)
        self.assertTrue(status)
        self.assertEqual(response,
                         b'\\title{Un pr\xe9}\n\\language{fr}\n\\author{Sophie Lemaire}\n\\email{'
                         b'soph'
                         b'ie.lemaire@math.u-psud.fr}\n\\computeanswer{no}\n\\precision{'
                         b'10000}\n\n\\in'
                         b'teger{L = 10*randint(1..10)}\n\\integer{l = 10*randint('
                         b'1..10)}\n\\integer{pe'
                         b"r = 2*(\\L+\\l)}\n\n\\statement{Donner le p\xe9rim\xe8tre d'un pr\xe9 "
                         b"rect"
                         b'angulaire\n de longueur \\L m et de largeur \\l m.}\n\n\\answer{'
                         b'p\xe9rim\xe8'
                         b'tre (en m)}{\\per}{type=numeric}\n')
    
    
    def test_getinfoserver(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getinfoserver()
        self.assertTrue(status)
        self.assertIn("server_version", response)
    
    
    def test_getlog(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getlog(9001, "myclass", "supervisor")
        self.assertTrue(status)
        self.assertIn("user_log", response)
    
    
    def test_getmodule(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getmodule('E1/geometry/oefsquare.fr')
        self.assertTrue(status)
        self.assertEqual(response['title'], "OEF Dessins")
    
    
    def test_getscore(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getscore(9001, "myclass", "supervisor")
        self.assertTrue(status)
        self.assertEqual(response['exam_scores'], [[]])
    
    
    def test_getscore_sheet(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getscore(9001, "myclass", "supervisor", 1)
        self.assertTrue(status)
        self.assertEqual(response['exam_scores'], [[]])
    
    
    def test_getscores(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getscores(9001, "myclass", ["login", "password", "name", "email"])
        self.assertTrue(status)
        self.assertEqual(response,
                         b'login;password;lastname;firstname;email\n"#";"Password";"Family '
                         b'name";"First (given) name";"email '
                         b'address"\n\n"quser";"password";"lastname";"firstn'
                         b'ame";"mail@mail.com"\n"user";"*Nv7lZCTkcYORw";"User";"user";""\n'
                         b'"anonymous";"anonymous";"Visiteur";"Anonyme";""\n')
    
    
    @unittest.skip("Job not defined in wims yet")
    def test_getsession(self):  # pragma: no cover
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getsession()
        self.assertTrue(status)
        self.assertTrue(False)
    
    
    @unittest.skip("Does not return a valid json")
    def test_getsheet(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getsheet(9001, "myclass", 3)
        self.assertTrue(status)
        self.assertEqual(response['sheet_title'], "Syntaxe des exercices OEF à réponse prédéfinie")
    
    
    def test_getsheetscores(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getsheetscores(9001, "myclass", 3)
        self.assertTrue(status)
        self.assertIn('data_scores', response)
    
    
    def test_getsheetstats(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getsheetstats(9001, "myclass", 3)
        self.assertTrue(status)
        self.assertIn("sheet_got_details", response)
    
    
    def test_gettime(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.gettime()
        self.assertTrue(status)
        self.assertIn("server_time", response)
    
    
    def test_getuser(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.getuser(9001, "myclass", "supervisor")
        self.assertTrue(status)
        self.assertEqual(response['firstname'], 'Sophie')
    
    
    def test_lightpopup(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.authuser(999999, "myclass", "supervisor")
        self.assertTrue(status)
        self.assertTrue('wims_session' in response)
        
        session = response['wims_session']
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.lightpopup(9001, "myclass", "supervisor", session,
                                          "H3/analysis/oeflinf.fr")
        self.assertTrue(status)
        self.assertIn(b'The exercises will be randomly selected fr'
                      b'om your selection \n(or otherwise from among all the available exercises '
                      b'if you didn\'t select any).', response)
    
    
    def test_linkexo(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.linkexo(999999, "myclass", 1, 1, 1)
        self.assertFalse(status)
        self.assertEqual(response["message"], "sheet 1 must be active")
    
    
    def test_linksheet(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.linksheet(999999, "myclass", 1, 1)
        self.assertFalse(status)
        self.assertEqual(response["message"], "sheet 1 must be active")
    
    
    def test_listclasses(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.listclasses("myclass")
        self.assertTrue(status)
        self.assertEqual(response["classes_list"], [{'qclass': '999999'}])
    
    
    def test_listexams(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.listexams(9001, "myclass")
        self.assertTrue(status)
        self.assertEqual(response["nbexam"], '0')
    
    
    def test_listexos(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.listexos(9001, "myclass")
        self.assertTrue(status)
        self.assertEqual(response["exocount"], 114)
    
    
    def test_listlinks(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.listlinks(9001, "myclass", 1, 1)
        self.assertFalse(status)
        self.assertEqual(response["message"],
                         "element #1 of type exam does not exist in this class (9001)")
    
    
    def test_listmodules(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.listmodules("H1")
        self.assertTrue(status)
        self.assertEqual(response["title"], 'Middle school year 1')
    
    
    def test_listsheets(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.listsheets(9001, "myclass")
        self.assertTrue(status)
        self.assertEqual(response["nbsheet"], "11")
    
    
    def test_modclass(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.modclass(999999, "myclass", {'description': "New title"})
        self.assertTrue(status)
        self.assertEqual(response["message"], 'Modifications done')
    
    
    def test_modexam(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.modexam(999999, "myclass", 1, {'title': "New title"})
        self.assertTrue(status)
        self.assertEqual(response["message"], '1 modifications done on exam 1.')
    
    
    def test_modsheet(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.modsheet(999999, "myclass", 1, {'title': "New title"})
        self.assertTrue(status)
        self.assertEqual(response["message"], '1 modifications done on sheet 1.')
    
    
    def test_moduser(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.moduser(999999, "myclass", "supervisor", {'firstname': "Newname"})
        self.assertTrue(status)
        self.assertEqual(response["message"], 'Modifications done')
    
    
    def test_movexo(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.movexo(9001, 999999, "myclass", 2, True)
        self.assertFalse(status)
        self.assertEqual(response["message"], 'COMPILATION ERROR No statement defined.')
    
    
    def test_movexos(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.movexos(9001, 999999, "myclass", True)
        self.assertTrue(status)
        self.assertEqual(response["message"], 'exercices successfully copied')
    
    
    @unittest.skip("Getting 'unauthorized' from WIMS")
    def test_putcsv(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.putcsv(999999, "myclass", CSV, False)
        self.assertTrue(status)
        self.assertEqual(response["message"], 'exercices successfully copied')
    
    
    @unittest.skip("Failing to import module")
    def test_putexo(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.putexo(999999, "myclass", 1, "H3/analysis/oeflinf.fr",
                                      {
                                          "exo"       : "fnctlin1", "qnum": "1",
                                          "scoredelay": "20,50",
                                          "seedrepeat": "2", "qcmlevel": "1"
                                      })
        self.assertTrue(status)
        self.assertEqual(response["message"], 'exercices successfully copied')
    
    
    def test_recuser(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.adduser(
            999999,
            "myclass",
            "jdoe3",
            {
                "lastname" : "Doe",
                "firstname": "Jhon",
                "password" : "password"
            }
        )
        self.assertTrue(status)
        self.assertEqual(response['message'], "user jdoe3 correctly added")
        
        status, response = api.deluser(999999, "myclass", "jdoe3")
        self.assertTrue(status)
        self.assertEqual(response['message'], "User jdoe3 moved to trash.")
        
        status, response = api.recuser(999999, "myclass", "jdoe3")
        self.assertTrue(status)
        self.assertEqual(response['message'], "job done. TODO : more explicit messages here...")
    
    
    def test_repairclass(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.repairclass(999999, "myclass")
        self.assertTrue(status)
        self.assertEqual(response['action,'], "checkonly")
    
    
    def test_sharecontent(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.addclass(
            999990,
            "myclass",
            {
                'description': "Test class",
                "institution": "Test institution",
                "supervisor" : "Test supervisor",
                "email"      : "Test@mail.com",
                "password"   : "password",
                "lang"       : "fr",
                "limit"      : 500
            },
            {
                "lastname" : "Doe",
                "firstname": "Jhon",
                "password" : "password"
            }
        )
        self.assertTrue(status)
        self.assertEqual(response['message'], "class 999990 correctly added")
        
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.sharecontent(9001, 999990, "myclass")
        self.assertTrue(status)
        self.assertEqual(response['message'], 'content successfully shared')
    
    
    def test_testexo(self):
        api = WimsAPI(WIMS_URL, "myself", "toto")
        status, response = api.testexo(
            b'\\title{Un pr\xe9}\n\\language{fr}\n\\author{Sophie Lemaire}\n\\email{'
            b'soph'
            b'ie.lemaire@math.u-psud.fr}\n\\computeanswer{no}\n\\precision{'
            b'10000}\n\n\\in'
            b'teger{L = 10*randint(1..10)}\n\\integer{l = 10*randint('
            b'1..10)}\n\\integer{pe'
            b"r = 2*(\\L+\\l)}\n\n\\statement{Donner le p\xe9rim\xe8tre d'un pr\xe9 "
            b"rect"
            b'angulaire\n de longueur \\L m et de largeur \\l m.}\n\n\\answer{'
            b'p\xe9rim\xe8'
            b'tre (en m)}{\\per}{type=numeric}\n')
        self.assertTrue(status)
        self.assertEqual(response['compilation_result'], "submit.oef.. -> submit.def")



if __name__ == '__main__':
    unittest.main
