import os
import http.client
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from auth import AuthError, requires_auth
from app import create_app
from models import setup_db, Movie, Actor


Assistant_header = {
     'Content-Type': 'application/json',
     'Authorization': "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkJMNXhBTEh4OUphV1Z4MVE5Tk14eSJ9.eyJpc3MiOiJodHRwczovL2Rldi03NW53dWphNy51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjE1NGFlZmMzM2Y2OTIwMDcwNDJiMzk2IiwiYXVkIjoiaHR0cHM6Ly9jYXBzdG9uZV9hcGkiLCJpYXQiOjE2MzI5Mzk5MTUsImV4cCI6MTYzMjk0NzExNSwiYXpwIjoiNFdTNjVuVlNzMFA2NUVzRER3RHVkRWhHSjNyWW1hMFQiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIl19.q0z8ihk-z1OjvDMBcVnW4XU-ljWG1qjds_QSjrn_pkmgBaxOwAiePhk9oD0Vy6oBI4WNohpo39cDFZ31r3nuDuVf0YCktwrpt6pI_iMdXQWmb9r_ylG--a6e4vgNffHSVagSrd8AVZ35yxdexa0pVB6gA2RY_wfTRcNnl07bHna3ZHfeWthI94LTrqzEORH7tJWpYA3ufPwMywHZsJVpXO5AmzZUOfrRwfDmjmjus0x2C5w1iV9IQrvFxMGFkvHlTzKkCq7KI_FsB3yVjRZ5EGJecpucYgx0T218ozjBGP31Id8RUfwUcjEExWxk7VG2dKv-gi4t6AhTN7Z0Oe2Q5Q"}


Director_header = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkJMNXhBTEh4OUphV1Z4MVE5Tk14eSJ9.eyJpc3MiOiJodHRwczovL2Rldi03NW53dWphNy51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjE1NGE0YzgzM2Y2OTIwMDcwNDJiMDY3IiwiYXVkIjoiaHR0cHM6Ly9jYXBzdG9uZV9hcGkiLCJpYXQiOjE2MzI5Mzk0NzksImV4cCI6MTYzMjk0NjY3OSwiYXpwIjoiNFdTNjVuVlNzMFA2NUVzRER3RHVkRWhHSjNyWW1hMFQiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTphY3RvciIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3IiLCJwYXRjaDptb3ZpZSIsInBvc3Q6YWN0b3IiXX0.sHjU2afVU_8WToJ6HH2VHvt99O-ZPBo9WiTyOn7DV9haGnyyd1TJBSdB4L_qsfwzcrQrZGSnB9vKgODv1Yogh_NdzB3TX_qBHJ7nRPNiwUbuUepW7sGNVcVrSkCLhMK4WiJrjHyGxz91Oa64U81BtQFak_64J4OSKJTq-LCuAPqc0nQmTjv_XofZMHqGAQxaVya7J42Zl-jSWDq9lGEZwG91L3fzmtGrjrdhMuBUK4ls16plNylH_QMqMknjIv9XuugLPmYkKYoQa653jjocorrgyEzLdgudD8a7fHCTe560dhTxNkClocpNugr7BADLgmJk_pnMpLFpLs-G4AT7cA'}

Executive_header = {
    'Content-Type': 'application/json',
    'Authorization': "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkJMNXhBTEh4OUphV1Z4MVE5Tk14eSJ9.eyJpc3MiOiJodHRwczovL2Rldi03NW53dWphNy51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjE1NGIxM2NjNjllYjIwMDcwNDkwNTFiIiwiYXVkIjoiaHR0cHM6Ly9jYXBzdG9uZV9hcGkiLCJpYXQiOjE2MzI5NDA0NjAsImV4cCI6MTYzMjk0NzY2MCwiYXpwIjoiNFdTNjVuVlNzMFA2NUVzRER3RHVkRWhHSjNyWW1hMFQiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTphY3RvciIsImRlbGV0ZTptb3ZpZSIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3IiLCJwYXRjaDptb3ZpZSIsInBvc3Q6YWN0b3IiLCJwb3N0Om1vdmllIl19.IMFfKdZsQDb9w8_je90EMDqpdWPu1VNWSaFCbrauIShJv-U3RXAWtq7k7KSxxNwJDh_511gPvy0dFqgJ89mttbTbcd9y0WsT6N37PnAQps43WNK-2V8LsYAwtHvoJ2xeYBq0u835DmYQc0XNtVukqsJ2T6KVxfZIM6LJT9LrSk4FhIkpaxbulMCWod-gIh2Je43O8pkRT737bGQszIxL2dHpnxaLubyRrGTC2mKBY4A9lImK-NgwVrPTo6v0kbybaFP13o7fF0CuiZXgr910dUEgeAAs_DXi6-HpaKZ778CZlRQjW-LLoL80WF3KUWsX5HR9xHhekL0OTYZ_JBGuZg"}

  

class Capstone_TestCase(unittest.TestCase):
    """This class represents the Capstone test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client
        self.database_name = "Capstone_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(
            'postgres', '4728', 'localhost:5432', self.database_name)
       
        setup_db(self.app, self.database_path)

        # self.director = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkJMNXhBTEh4OUphV1Z4MVE5Tk14eSJ9.eyJpc3MiOiJodHRwczovL2Rldi03NW53dWphNy51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjEyYTlmMzlhYWFiMmYwMDZhZTA5ZjE3IiwiYXVkIjoiaHR0cHM6Ly9jYXBzdG9uZV9hcGkiLCJpYXQiOjE2MzI5MzI1MDAsImV4cCI6MTYzMjkzOTcwMCwiYXpwIjoiNFdTNjVuVlNzMFA2NUVzRER3RHVkRWhHSjNyWW1hMFQiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTphY3RvciIsImRlbGV0ZTptb3ZpZSIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3IiLCJwYXRjaDptb3ZpZSIsInBvc3Q6YWN0b3IiLCJwb3N0Om1vdmllIl19.baNU_5EIH_UJweMdjROssc53MrhRGZwKc8mpOj2Gr4dJOgnYJt9Smrat_65Nz4LRV3J19HWKOuINctb32Fq4kh-8goFDyElmsBwiWV1u3uq9VWlIyTWvHUUZTBW2fWWJhK3BY_LoRt_US03-aAhPB140ygFzAq06JQmRp3uwBMEVIPT7O2KERyCnrghclUZbWzXez2i3AGL7Pc-fkLPNrfrCeLpyp4svm9VpWLqtFjMVRtrgTBe9dHed9cxxK-6tcBXQTQ8kcHoYDpGujD1VeuyK3bIUFtfMzr2oDjSLvMVq0KAWwjMfnlo_xEeIw5dge_dD-y-u59vL9sBZ1fMWYw'
        # self.headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+ self.director}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    
    def tearDown(self):
        """Executed after reach test"""
        pass       
    


    #---Movies_TestCases
    
    
    def test_post_movie(self):
        res = self.client().post('/movies', json={
            'title': "Answer",
            'release_date': "2021-02-17 21:30:11.000000"}, headers=Executive_header )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Movie successfully posted')

    def test_get_movies(self):
        res = self.client().get('/movies', headers=Executive_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    def test_invalid_get_movies(self):
        res = self.client().get('/movies')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
    
    
    
    def test_invalid_post_movie(self):
        res = self.client().post('/movies', headers= Executive_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Movie not posted')


    def test_patch_movie(self):
        res = self.client().patch('/movies/2', headers= Executive_header, json={
            'title': 'new title'
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Movie successfully updated')
    
    def test_invalid_patch_movie(self):
        res = self.client().patch('/movies/2', headers= Director_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Movie not updated')

    def test_unauthorised_patch_movie(self):
        res = self.client().patch('/movies/2', headers= Assistant_header, json={
            'title': 'new title'
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)


    def test_delete_movie(self):
        res = self.client().delete('/movies/1', headers=Executive_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('delete', data)
        self.assertEqual(data['message'], 'Movie successfully deleted')
    

    def test_invalid_delete_movie(self):
        res = self.client().delete('/movies/1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)




    #---Actors_TestCases


    def test_get_actors(self):
        res = self.client().get('/actors', headers= Executive_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    def test_invalid_get_actors(self):
        res = self.client().get('/actors')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)


    def test_post_actor(self):
        res = self.client().post('/actors', json={
            'name': "ziad",
            'age': "22",
            'gender': "male"  }, headers= Executive_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Actor successfully posted')
    
    
    def test_invalid_post_actor(self):
        res = self.client().post('/actors', headers= Executive_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Actor not posted')


    def test_patch_actor(self):
        res = self.client().patch('/actors/1', headers= Executive_header, json={
            'name': 'new name'
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Actor successfully updated')
    
    def test_invalid_patch_actor(self):
        res = self.client().patch('/actors/1', headers= Director_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Actor not updated')

    def test_unauthorised_patch_actor(self):
        res = self.client().patch('/actors/2', headers= Assistant_header, json={
            'name': 'new name'
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)


    def test_delete_actor(self):
        res = self.client().delete('/actors/1', headers= Director_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('delete', data)
        self.assertEqual(data['message'], 'Actor successfully deleted')
    

    def test_invalid_delete_actor(self):
        res = self.client().delete('/actors/1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)


if __name__ == "__main__":
    unittest.main()