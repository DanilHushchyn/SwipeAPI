import pytest
from model_bakery import baker
from client.models import ChatMessage
from users.models import CustomUser

pytestmark = pytest.mark.django_db


class TestMessage:
    @pytest.mark.parametrize("payload,expected_status",
                             [
                                 ({
                                      "id": 1,
                                      "content": "Hello World",
                                      "recipient": 10,
                                  }, 200),
                                 ({
                                      "id": 2,
                                      "content": "I'm a god",
                                      "recipient": 11,
                                  }, 200),
                                 ({
                                      "id": 3,
                                      "content": "How are you?",
                                      "recipient": 10,
                                  }, 200),
                             ]
                             )
    def test_create_message(self, payload, expected_status, client):
        client_api, client = client
        baker.make(CustomUser, id=10)
        baker.make(CustomUser, id=11)
        response = client_api.post('/api/v1/client/messages/', payload, format='multipart')
        assert response.status_code == expected_status, f'Status code expected {expected_status} but got {response.status_code}'
        assert response.data['content'] == payload['content'], \
            f" Field content expected {payload['content']} but got {response.data['content']}"
        assert response.data['recipient'] == payload['recipient'], \
            f" Field recipient expected {payload['recipient']} but got {response.data['recipient']}"

    @pytest.mark.parametrize("id,expected_status", [(10, 204), (1, 404), ])
    def test_destroy_message(self, id, expected_status, client):
        client_api, client = client
        baker.make(ChatMessage, id=10)
        response = client_api.delete(f'/api/v1/client/messages/{id}/', format='multipart')
        assert response.status_code == expected_status, f'Status code expected {expected_status} but got {response.status_code}'

    @pytest.mark.parametrize("id,expected_status", [(10, 200), (1, 404), ])
    def test_partial_update_message(self, id, expected_status, client):
        client_api, client = client
        baker.make(ChatMessage, id=10)
        payload = {
            "content": "Updated message!!!",
        }
        response = client_api.patch(f'/api/v1/client/messages/{id}/', payload, format='multipart')
        assert response.status_code == expected_status, f'Status code expected {expected_status} but got {response.status_code}'
        if expected_status == 200:
            assert response.data['content'] == payload['content'], \
                f" Field content expected {payload['content']} but got {response.data['content']}"
