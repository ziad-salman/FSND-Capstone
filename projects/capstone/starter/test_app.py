import os
import http.client
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from auth import AuthError, requires_auth
from app import create_app
from models import setup_db, Movie, Actor


# Assistant_header = {
#     'Content-Type': 'application/json',
#     'Authorization': "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkJMNXhBTEh4OUphV1Z4MVE5Tk14eSJ9.eyJpc3MiOiJodHRwczovL2Rldi03NW53dWphNy51cy5hdXRoMC5jb20vIiwic3ViIjoiMEV1RXFLd1hmRUo5c1ZNMFBSZUttTko4RmEzeTdVNHVAY2xpZW50cyIsImF1ZCI6Imh0dHBzOi8vY2Fwc3RvbmVfYXBpIiwiaWF0IjoxNjMyODI1NTU2LCJleHAiOjE2MzI5MTE5NTYsImF6cCI6IjBFdUVxS3dYZkVKOXNWTTBQUmVLbU5KOEZhM3k3VTR1Iiwic2NvcGUiOiJnZXQ6bW92aWVzIGdldDphY3RvcnMiLCJndHkiOiJjbGllbnQtY3JlZGVudGlhbHMiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6bW92aWVzIiwiZ2V0OmFjdG9ycyJdfQ.aJ22V4MXe7Hy5cCYF79admLatpljGFEBWlZoOFNRONivpP7keR_O-MiGuoLWc4n8Kpkt9pWOCRjTvOFc-gizYMfriTz7IRd5heiDEBWry2BfzXyHFxaFn0_LUDdGKgiIUaKqmJkXqiUpf_S8w2hOcvnPswfuwoLhHeu7D-b9emoU2Ctl9Phvm-Mr-fEHjyBKP9LfcEq345Z_A8TfjUY5OBShYBAFegQEk0j_MJ32-KViNvgsFQ5yzOFbw5jrbBfwX3IP7bTMwJnPXpGPNf2cLwDCWQvc8c_1o9pmzXD9qt04ew-h6VzWGW8_7FQYL6S1TkqMQ5SOtuRkhlAzoRnyzg"}


# Executive_header = {
#     'Content-Type': 'application/json',
#     'Authorization': "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkJMNXhBTEh4OUphV1Z4MVE5Tk14eSJ9.eyJpc3MiOiJodHRwczovL2Rldi03NW53dWphNy51cy5hdXRoMC5jb20vIiwic3ViIjoiS2NsWFRtcE9DbTNpcTc3QnAwRmwyZlJ0Q05wWnh3RVFAY2xpZW50cyIsImF1ZCI6Imh0dHBzOi8vY2Fwc3RvbmVfYXBpIiwiaWF0IjoxNjMyODI2MjY3LCJleHAiOjE2MzI5MTI2NjcsImF6cCI6IktjbFhUbXBPQ20zaXE3N0JwMEZsMmZSdENOcFp4d0VRIiwic2NvcGUiOiJnZXQ6bW92aWVzIHBvc3Q6bW92aWUgcGF0Y2g6bW92aWUgZGVsZXRlOm1vdmllIGdldDphY3RvcnMgcG9zdDphY3RvciBwYXRjaDphY3RvciBkZWxldGU6YWN0b3IiLCJndHkiOiJjbGllbnQtY3JlZGVudGlhbHMiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6bW92aWVzIiwicG9zdDptb3ZpZSIsInBhdGNoOm1vdmllIiwiZGVsZXRlOm1vdmllIiwiZ2V0OmFjdG9ycyIsInBvc3Q6YWN0b3IiLCJwYXRjaDphY3RvciIsImRlbGV0ZTphY3RvciJdfQ.avTdwS4k9uNfoCNbezST98d__KsnEELx6QWhvj-1EfQD7h_S8Yv-rgemwD5TjI4IO-64AXExeOlF6JMsR1oL2gbRIFmnLe2GWtFaw55fVzPmrWkWN73NUCwjZyT6kNjgzVMgQLyn2dblkIW-iPpxkfPYc1Lnvps44LvMWOJylgaKRB6RJQfB2BHArg_Bs4u0zam6xxzqedBN1-A7hfBEmH6fupzddSJFgHOqtTFxTP-fITTPQ7pIV86gL7Z9cAQfTIb7NKwsclOuwp9fTq2j1MysvPfypw5lek8eGwZhsukTBesgzLARCMoBDq54Al9WwsaSs-AyGfLjjo_ZsYm1QQ"}

# Director_header = {
#     'Content-Type': 'application/json',
#     'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkJMNXhBTEh4OUphV1Z4MVE5Tk14eSJ9.eyJpc3MiOiJodHRwczovL2Rldi03NW53dWphNy51cy5hdXRoMC5jb20vIiwic3ViIjoiNU51dms5cWRnUWFWZklQRUdRN2RXdEZBNUc3bVQ2MmJAY2xpZW50cyIsImF1ZCI6Imh0dHBzOi8vY2Fwc3RvbmVfYXBpIiwiaWF0IjoxNjMyNzA1Mzk4LCJleHAiOjE2MzI3OTE3OTgsImF6cCI6IjVOdXZrOXFkZ1FhVmZJUEVHUTdkV3RGQTVHN21UNjJiIiwic2NvcGUiOiJnZXQ6bW92aWVzIHBhdGNoOm1vdmllIGdldDphY3RvcnMgcG9zdDphY3RvciBwYXRjaDphY3RvciBkZWxldGU6YWN0b3IiLCJndHkiOiJjbGllbnQtY3JlZGVudGlhbHMiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6bW92aWVzIiwicGF0Y2g6bW92aWUiLCJnZXQ6YWN0b3JzIiwicG9zdDphY3RvciIsInBhdGNoOmFjdG9yIiwiZGVsZXRlOmFjdG9yIl19.iMavgym7Vwat10TtgKoMxif1gjUxFEo-4TEJm_v8glIdM41lSq7bvAUEF2Yq4B7mipomV_kbyhcTGe_-SfAYlAvc1gFh7IWkgsFP37NDsYgIwMjcB-CtoVhywooDIioN5eWmJ6_xPnyvGA_QnQzOrTkiA0W_8pZUpAHO7CKDRP_YHPAfVNW1QbKDONRigWy0v3t2bAHdKE3Wz9rCWuke5GeFnhIIBH85AZaSFGNki-YOesK25dYO8Q1ST4U6-LavZoYvMo1S_tLuEn-0HnyMjWRuIXnm_tfTkeHnb8imzLtyOUNI8CQnZY3Eocm86SIXJdRid8GmjfgIsfNrKfV9Kg'}

  

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

        self.director = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkJMNXhBTEh4OUphV1Z4MVE5Tk14eSJ9.eyJpc3MiOiJodHRwczovL2Rldi03NW53dWphNy51cy5hdXRoMC5jb20vIiwic3ViIjoiS2NsWFRtcE9DbTNpcTc3QnAwRmwyZlJ0Q05wWnh3RVFAY2xpZW50cyIsImF1ZCI6Imh0dHBzOi8vY2Fwc3RvbmVfYXBpIiwiaWF0IjoxNjMyODUxNzIzLCJleHAiOjE2MzI5MzgxMjMsImF6cCI6IktjbFhUbXBPQ20zaXE3N0JwMEZsMmZSdENOcFp4d0VRIiwic2NvcGUiOiJnZXQ6bW92aWVzIHBvc3Q6bW92aWUgcGF0Y2g6bW92aWUgZGVsZXRlOm1vdmllIGdldDphY3RvcnMgcG9zdDphY3RvciBwYXRjaDphY3RvciBkZWxldGU6YWN0b3IgR0VUOm1vdmllcyBQT1NUOm1vdmllIiwiZ3R5IjoiY2xpZW50LWNyZWRlbnRpYWxzIiwicGVybWlzc2lvbnMiOlsiZ2V0Om1vdmllcyIsInBvc3Q6bW92aWUiLCJwYXRjaDptb3ZpZSIsImRlbGV0ZTptb3ZpZSIsImdldDphY3RvcnMiLCJwb3N0OmFjdG9yIiwicGF0Y2g6YWN0b3IiLCJkZWxldGU6YWN0b3IiLCJHRVQ6bW92aWVzIiwiUE9TVDptb3ZpZSJdfQ.bXYcb5X4ap03fo5CWR-ZGny8YFMQZrru-f-iVnNroDyBBdeG31H3FTL_isizW8VMXmlu4rG_AXEv71OF1hgdzolxt32QD50y-VMlH3ZE0d2ytDQAxsAhdEadd9mHloN61E1Sktt6DJnYhGCSqBEjpcaiaIurUdhAfJ_sYqRj8FHnTpEC9nf-sPFpmxF21iu4nRKaU-am52hd73AQMmr_0UwJ5Z8bgJpKlN9DKklh3UoFRYQiW5UWtPt0GQUt6jIuMQKRYWXQpog_VqQH5uLBlraLP8jJy07uGALdExCARUJeukK1HAnJ4d9A5iVUazIvlYNvu_zKQDJGy77lHXupYA'
        self.headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+ self.director}

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
            'release_date': "2021-02-17 21:30:11.000000"}, headers= self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Movie successfully posted')

    def test_get_movies(self):
        res = self.client().get('/movies', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    def test_invalid_get_movies(self):
        res = self.client().get('/movies')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)


    
    
    
    def test_invalid_post_movie(self):
        res = self.client().post('/movies', headers= self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Movie not posted')


    def test_patch_movie(self):
        res = self.client().patch('/movies/2', headers= self.headers, json={
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
        res = self.client().delete('/movies/1', headers=self.headers)
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
        res = self.client().get('/actors', headers= self.headers)
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