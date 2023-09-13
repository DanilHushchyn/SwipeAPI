import pytest
from model_bakery import baker
from client.models import ChatMessage, Announcement, Complaint, Filter
from users.models import CustomUser

pytestmark = pytest.mark.django_db


class TestFilter:
    @pytest.mark.parametrize("payload,expected_status",
                             [
                                 ({
                                      "address": "string",
                                      "layout": "Европланировка",
                                      "grounds_doc": "Собственность",
                                      "room_count": "1",
                                      "min_price": 100,
                                      "max_price": 1000,
                                      "min_square": 50,
                                      "max_square": 500,
                                      "appointment": "Квартира",
                                      "payment_type": "Ипотека",
                                      "condition": "Черновая"
                                  }, 201),
                                 ({
                                      "address": "string",
                                      "layout": "Классическая",
                                      "grounds_doc": "Собственность",
                                      "room_count": "2",
                                      "min_price": 100,
                                      "max_price": 1000,
                                      "min_square": 50,
                                      "max_square": 500,
                                      "appointment": "Дом",
                                      "payment_type": "Ипотека",
                                      "condition": "Ремонт от застройщика"
                                  }, 201),
                                 ({
                                      "address": "string",
                                      "layout": "Студия, санузел",
                                      "grounds_doc": "Собственность",
                                      "room_count": "3",
                                      "min_price": 100,
                                      "max_price": 1000,
                                      "min_square": 50,
                                      "max_square": 500,
                                      "appointment": "Офисное помещение",
                                      "payment_type": "Ипотека",
                                      "condition": "В жилом состоянии"
                                  }, 201),
                                 ({
                                      "address": "string",
                                      "layout": "Студия, санузел",
                                      "grounds_doc": "Собственность",
                                      "room_count": "3",
                                      "min_price": 100,
                                      "max_price": 1000,
                                      "min_square": 50,
                                      "max_square": 500,
                                      "appointment": "Хз",
                                      "payment_type": "Ипотека",
                                      "condition": "Черновая"
                                  }, 400),
                                 ({
                                      "address": "string",
                                      "layout": "Обычная",
                                      "grounds_doc": "Собственность",
                                      "room_count": "3",
                                      "min_price": 100,
                                      "max_price": 1000,
                                      "min_square": 50,
                                      "max_square": 500,
                                      "appointment": "Хз",
                                      "payment_type": "Ипотека",
                                      "condition": "Без понятия"
                                  }, 400),
                             ]
                             )
    def test_create_filter(self, payload, expected_status, client):
        client_api, client = client
        announcement = baker.make(Announcement)
        payload['announcement'] = announcement.id
        response = client_api.post('/api/v1/client/filters/', payload, format='json')
        assert response.status_code == expected_status, f'Status code expected {expected_status} but got {response.status_code}'

    def test_list_filters(self, client):
        client_api, client = client
        baker.make(Filter, client=client, _quantity=5)
        response = client_api.get('/api/v1/client/filters/', format='json')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        assert len(response.data) == 5, f'Status code expected {5} but got {len(response.data)}'

    def test_retrieve_filter(self, client):
        client_api, client = client
        filter = baker.make(Filter, client=client)
        response = client_api.get(f'/api/v1/client/filters/{filter.id}/', format='json')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        response = client_api.get(f'/api/v1/client/filters/{filter.id + 1}/', format='json')
        assert response.data == "Фильтр не найден", f'Status code expected {"Фильтр не найден"} but got {response.data}'

    def test_delete_filter(self, client):
        client_api, client = client
        filter = baker.make(Filter, client=client)
        response = client_api.delete(f'/api/v1/client/filters/{filter.id}/', format='json')
        assert response.status_code == 204, f'Status code expected {204} but got {response.status_code}'
        response = client_api.delete(f'/api/v1/client/filters/{filter.id + 1}/', format='json')
        assert response.status_code == 404, f'Status code expected {404} but got {response.status_code}'

    def test_filter_announcements_list(self, client):
        client_api, client = client
        filter_payload = {
            "condition": "Черновая"
        }
        baker.make(Announcement, living_condition='Черновая', _quantity=5)
        baker.make(Announcement, living_condition='В жилом состоянии', _quantity=3)
        filter = baker.make(Filter, client_id=client.id, **filter_payload)
        response = client_api.get(f'/api/v1/client/filters/{filter.id}/announcements_list/', format='json')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        assert response.data[
                   "announcements_count"] == 5, f'Status code expected {5} but got {response.data["announcements_count"]}'
