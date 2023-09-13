import pytest
from model_bakery import baker
from client.models import ChatMessage, Announcement, Complaint
from users.models import CustomUser

pytestmark = pytest.mark.django_db


class TestComplaint:
    @pytest.mark.parametrize("payload,expected_status",
                             [
                                 ({
                                      "description": "string",
                                      "complaint_reason": "Мошенничество",
                                      "announcement": 2
                                  }, 200),
                                 ({
                                      "description": "string",
                                      "complaint_reason": "Некорректное фото",
                                      "announcement": 2
                                  }, 200),
                                 ({
                                      "description": "string",
                                      "complaint_reason": "Некорректное всё",
                                      "announcement": 2
                                  }, 400),
                             ]
                             )
    def test_create_complaint(self, payload, expected_status, client):
        client_api, client = client
        announcement = baker.make(Announcement)
        payload['announcement'] = announcement.id
        response = client_api.post('/api/v1/client/complaints/', payload, format='json')
        assert response.status_code == expected_status, f'Status code expected {expected_status} but got {response.status_code}'

    def test_get_complaints_for_announcement(self, client):
        client_api, client = client
        announcement = baker.make(Announcement)
        baker.make(Complaint, announcement_id=announcement.id, _quantity=3)

        response = client_api.get(f'/api/v1/client/complaints/announcement_complaint_list/{announcement.id}/',
                                  format='json')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        response = client_api.get(f'/api/v1/client/complaints/announcement_complaint_list/{100}/',
                                  format='json')
        assert response.data == [], f'Status code expected {[]} but got {response.data}'
