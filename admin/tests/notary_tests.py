# content of test_sample.py
import base64

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from admin.models import Notary
from users.models import CustomUser

pytestmark = pytest.mark.django_db


class TestNotary:

    def test_create_notary(self, admin, client_api):
        client_api.force_authenticate(user=admin)
        image_path = "media/data_for_testing/img.png"

        payloads = [
            {
                "id": 1,
                "first_name": "Notary",
                "last_name": "Green",
                "email": "notary1@gmail.com",
                "phone": "+38 (098) 567-81-23"
            },
            {
                "id": 2,
                "first_name": "Notary",
                "last_name": "Red",
                "email": "notary2@gmail.com",
                "phone": "+38 (098) 567-81-12"
            },
            {
                "id": 3,
                "first_name": "Notary",
                "last_name": "Cliff",
                "email": "user@example.com",
                "phone": "+38 (098) 567-81-11",
            },
        ]
        for payload in payloads:
            image_file = open(image_path, "rb")
            image_data = SimpleUploadedFile(image_file.name, image_file.read())
            payload['avatar'] = image_data
            response = client_api.post('/api/v1/moderation/notaries/', payload, format='multipart')
            # data = response.data[0]
            assert response.status_code == 201, f'Status code expected {201} but got {response.status_code}'
            assert response.data['first_name'] == payload['first_name'], \
                f" Field first_name expected {payload['first_name']} but got {response.data['first_name']}"
            assert response.data['last_name'] == payload['last_name'], \
                f" Field last_name expected {payload['last_name']} but got {response.data['last_name']}"
            assert response.data['email'] == payload['email'], \
                f" Field email expected {payload['email']} but got {response.data['email']}"
            assert response.data['phone'] == payload['phone'], \
                f" Field phone expected {payload['phone']} but got {response.data['phone']}"

    def test_list_notary(self, admin, client_api):
        baker.make(Notary, _quantity=5)
        client_api.force_authenticate(user=admin)
        response = client_api.get('/api/v1/moderation/notaries/')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        assert Notary.objects.all().count() == 5, f'Notaries count expected {3} but got {Notary.objects.all().count()}'

    def test_retrieve_notary(self, admin, client_api):
        baker.make(Notary, id=10)
        client_api.force_authenticate(user=admin)
        response = client_api.get('/api/v1/moderation/notaries/10/', format='multipart')
        assert response.status_code == 200

    def test_destroy_notary(self, admin, client_api):
        baker.make(Notary, id=10)
        client_api.force_authenticate(user=admin)
        response = client_api.delete('/api/v1/moderation/notaries/10/')
        assert response.status_code == 204, f'Status code expected {204} but got {response.status_code}'

    def test_partial_update_notary(self, admin, client_api):
        baker.make(Notary, id=10)
        client_api.force_authenticate(user=admin)
        payload = {
            "first_name": "Tom",
            "last_name": "Hanks",
        }
        response = client_api.patch('/api/v1/moderation/notaries/1/', payload, format='multipart')
        assert response.status_code == 404, f'Status code expected {404} but got {response.status_code}'
        response = client_api.patch('/api/v1/moderation/notaries/10/', payload, format='multipart')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        assert response.data['first_name'] == payload['first_name'], \
            f" Field first_name expected {payload['first_name']} but got {response.data['first_name']}"
        assert response.data['last_name'] == payload['last_name'], \
            f" Field last_name expected {payload['last_name']} but got {response.data['last_name']}"
