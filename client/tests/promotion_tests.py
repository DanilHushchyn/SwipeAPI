import pytest
from model_bakery import baker

from client.models import Announcement, Promotion
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


class TestPromotion:
    @pytest.mark.parametrize("payload,expected_status",
                             [

                                 ({
                                      "is_active": True,
                                      "phrase": True,
                                      "highlight": True,
                                      "highlight_color": "Розовый",
                                      "phrase_content": "Подарок при покупке",
                                      "big_advert": True,
                                      "turbo": True,
                                      "raise_advert": True,
                                      "price": 10_000,
                                      "announcement": 1
                                  }, 201),
                                 ({
                                      "is_active": True,
                                      "phrase": True,
                                      "highlight": True,
                                      "highlight_color": "Розовый",
                                      "phrase_content": "Подарок при покупке",
                                      "big_advert": True,
                                      "turbo": True,
                                      "raise_advert": True,
                                      "price": 100_000,
                                      "announcement": 2
                                  }, 201),
                                 ({
                                      "is_active": True,
                                      "phrase": False,
                                      "highlight": True,
                                      "highlight_color": "Розовый",
                                      "phrase_content": "Подарок при покупке",
                                      "big_advert": False,
                                      "turbo": True,
                                      "raise_advert": True,
                                      "price": 150,
                                  }, 400),
                             ]
                             )
    def test_create_promotion(self, payload, expected_status, client):
        client_api, client = client
        baker.make(Announcement, id=1)
        baker.make(Announcement, id=2)
        response = client_api.post('/api/v1/client/promotions/', payload, format='json')
        assert response.status_code == expected_status, f'Status code expected {expected_status} but got {response.status_code}'

