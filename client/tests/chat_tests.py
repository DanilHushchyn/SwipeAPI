import pytest
from model_bakery import baker
from client.models import ChatMessage, Chat
from users.models import CustomUser

pytestmark = pytest.mark.django_db


class TestChat:
    @pytest.mark.parametrize("id,expected_status", [(10, 200), (1, 404), ])
    def test_get_chat_messages(self, id, expected_status, client):
        client_api, client = client
        recipient = baker.make(CustomUser, id=10)
        chat = baker.make(Chat, id=10)
        baker.make(ChatMessage, recipient=recipient, chat=chat, _quantity=5)
        response = client_api.get(f'/api/v1/client/chats/{id}/', format='json')
        assert response.status_code == expected_status, f'Status code expected {expected_status} but got {response.status_code}'
        if expected_status == 200:
            assert len(response.data['messages']) == 5, \
                f'Messages count expected {5} but got {len(response.data["messages"])}'

    def test_get_my_chats(self, client):
        client_api, client = client
        for i in range(5):
            chat = baker.make(Chat)
            chat.users.set([1, ])
        response = client_api.get(f'/api/v1/client/chats/', format='json')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        assert len(response.data) == 5, \
            f'Messages count expected {5} but got {len(response.data)}'

    @pytest.mark.parametrize("id,expected_status", [(10, 204), (1, 404), ])
    def test_delete_chat(self, id, expected_status, client):
        client_api, client = client
        baker.make(Chat, id=10)
        response = client_api.delete(f'/api/v1/client/chats/{id}/', format='json')
        assert response.status_code == expected_status, f'Status code expected {expected_status} but got {response.status_code}'
