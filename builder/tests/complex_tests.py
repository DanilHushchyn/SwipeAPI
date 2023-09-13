import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from client.models import Announcement

pytestmark = pytest.mark.django_db


class TestComplex:
    @pytest.mark.parametrize("payload,expected_status",
                             [
                                 (
                                         {
                                             "title": "Жк Миллениум",
                                             "description": "Описание",
                                             "status": "Квартиры",
                                             "level": "Стандарт",
                                             "type": "Многоквартирный",
                                             "material_type": "Монолитно-панельное",
                                             "perimeter_status": "Закрытая",
                                             "sea_destination_m": 0,
                                             "ceiling_height_m": 0,
                                             "gas": True,
                                             "heating": "Центральное",
                                             "electricity": True,
                                             "water_supply": "Центральное",
                                             "sewerage": "Центральная",
                                             "payment_type": "Мат.капитал",
                                             "price_in_contract": "123",
                                         }, 200),
                             ]
                             )
    def test_create_complex(self, payload, expected_status, builder):
        client_api, builder = builder
        image_path = "media/data_for_testing/img.png"
        image_file = open(image_path, "rb")
        image_data = SimpleUploadedFile(image_file.name, image_file.read())
        payload['gallery'] = [image_data, ]
        payload['dockit'] = [image_data, ]
        response = client_api.post('/api/v1/builder/complexes/', payload, format='multipart')
        assert response.status_code == expected_status, f'Status code expected {expected_status} but got {response.status_code}'
