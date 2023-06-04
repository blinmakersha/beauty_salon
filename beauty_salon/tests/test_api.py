from json import dumps

from beauty_salon_app.models import Doctor, Service
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class ViewSetsTests(TestCase):
    pages = (
            (Doctor, '/rest/Doctor/', {
                "name": "name",
                "surname": "surname",
                "speciality": "speciality",
                "description": "description",
                "sex": "-",
                "phone": "+79123456789",
                "office": "101"
            }, {"sex": "M"}),
        (Service, '/rest/Service/', {
            "title": "title",
            "description": "description",
            "duration": "30",
            "price": "100"
        }, {"description": "descr"}),
    )

    def setUp(self):
        self.client = Client()
        self.creds_superuser = {'username': 'super',
                                'email': 'super@super.com', 'password': 'super'}
        self.creds_user = {'username': 'default', 'password': 'default'}
        self.superuser = User.objects.create_user(
            is_superuser=True, **self.creds_superuser)
        self.user = User.objects.create_user(**self.creds_user)
        self.token = Token.objects.create(user=self.superuser)

    def test_get(self):
        # logging in with superuser creds
        self.client.login(**self.creds_user)
        # GET
        for _, url, _, _ in self.pages:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # logging out
        self.client.logout()

    def manage(self, auth_token=False):
        for cls_model, url, data, to_change in self.pages:
            # POST
            resp_post = self.client.post(url, data=data)
            #print(resp_post)
            self.assertEqual(resp_post.status_code, status.HTTP_201_CREATED)
            created_id = cls_model.objects.get(**data).id
            # PUT
            if not auth_token:
                data = to_change if auth_token else dumps(to_change)
                resp_put = self.client.put(
                    f'{url}?id={created_id}',
                    data=dumps(to_change),
                )
                self.assertEqual(resp_put.status_code, status.HTTP_200_OK)
                attr, value = list(to_change.items())[0]
                self.assertEqual(
                    getattr(cls_model.objects.get(id=created_id), attr), value)
            # DELETE EXISTING
            resp_delete = self.client.delete(f'{url}?id={created_id}')
            self.assertEqual(resp_delete.status_code,
                             status.HTTP_204_NO_CONTENT)
            # DELETE NONEXISTENT
            repeating_delete = self.client.delete(f'{url}?id={created_id}')
            self.assertEqual(repeating_delete.status_code,
                             status.HTTP_404_NOT_FOUND)

    def test_manage_superuser(self):
        # logging in with superuser creds
        self.client.login(**self.creds_superuser)

        self.manage()

        # logging out
        self.client.logout()

    def test_manage_user(self):
        # logging in with superuser creds
        self.client.login(**self.creds_user)
        for cls_model, url, data, to_change in self.pages:
            # POST
            resp_post = self.client.post(url, data=data)
            self.assertEqual(resp_post.status_code, status.HTTP_403_FORBIDDEN)
            # PUT
            created = cls_model.objects.create(**data)
            resp_put = self.client.put(
                f'{url}?id={created.id}',
                data=dumps(to_change),
                # content_type='text/json'
            )
            #print(f'RESP PUT CONTENT: {resp_put.content}')
            self.assertEqual(resp_put.status_code, status.HTTP_403_FORBIDDEN)
            # DELETE EXISTING
            resp_delete = self.client.delete(f'{url}?id={created.id}')
            self.assertEqual(resp_delete.status_code,
                             status.HTTP_403_FORBIDDEN)
            # clean up
            created.delete()
        # logging out
        self.client.logout()

    def test_manage_token(self):
        # creating rest_framework APIClient instead of django test Client
        # because it can be forcefully authenticated with token auth
        self.client = APIClient()

        self.client.force_authenticate(user=self.superuser, token=self.token)
        self.manage(auth_token=True)
