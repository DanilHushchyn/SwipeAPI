import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from builder.models import Complex
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
        file_path = "media/data_for_testing/Dronov.pdf"
        image_file = open(image_path, "rb")
        file = open(file_path, "rb")
        image_data = SimpleUploadedFile(image_file.name, image_file.read())
        file_data = SimpleUploadedFile(file.name, file.read())
        payload['gallery'] = [image_data, ]
        payload['dockit'] = [file_data, ]
        response = client_api.post('/api/v1/builder/complexes/', payload, format='multipart')
        assert response.status_code == expected_status, f'Status code expected {expected_status} but got {response.status_code}'

    def test_update_complex(self, builder):
        client_api, builder = builder
        data_for_update = {
            "title": "ЖК Миллениум",
            "description": "Описание ЖК",
        }
        baker.make(Complex, builder=builder,id=5)

        response = client_api.patch(f'/api/v1/builder/complexes/update_my_complex/', data_for_update, format='multipart')

        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        assert response.data["title"] == data_for_update[
            "title"], f'Field title expected {data_for_update["title"]} but got {response.data["title"]}'
        assert response.data["description"] == data_for_update[
            "description"], f'Field description expected {data_for_update["description"]} but got {response.data["description"]}'

    def test_switch_announcement_favorite(self, builder):
        client_api, builder = builder
        obj = baker.make(Complex)
        response = client_api.post(f'/api/v1/builder/complexes/{obj.id}/switch_complex_favorite/',
                                   format='multipart')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        assert response.data == "Успешно добавлен", "Add complex to favorite doesn't work"
        response = client_api.post(f'/api/v1/builder/complexes/{obj.id}/switch_complex_favorite/',
                                   format='multipart')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        assert response.data == "Успешно удалён", "Remove complex from favorite doesn't work"

    def test_my_favorite_complexes_list(self, builder):
        client_api, builder = builder
        for i in range(5):
            complex = baker.make(Complex)
            builder.favorite_complexes.add(complex.id)
        response = client_api.get(f'/api/v1/builder/complexes/my_favorite_complexes/',
                                  format='multipart')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        assert len(response.data) == 5, f'Status code expected {5} but got {len(response.data)}'

    def test_get_my_complex(self, builder):
        client_api, builder = builder
        baker.make(Complex, builder=builder)
        response = client_api.get(f'/api/v1/builder/complexes/my_complex/',
                                  format='multipart')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'

    def test_list_complexes(self, builder):
        client_api, builder = builder
        baker.make(Complex, _quantity=10)
        response = client_api.get(f'/api/v1/builder/complexes/',
                                  format='multipart')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        assert len(response.data) == 10, f'Status code expected {10} but got {len(response.data)}'

    def test_retrieve_complexes(self, builder):
        client_api, builder = builder
        complex = baker.make(Complex)
        response = client_api.get(f'/api/v1/builder/complexes/{complex.id}/',
                                  format='multipart')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        response = client_api.get(f'/api/v1/builder/complexes/{complex.id + 1}/',
                                  format='multipart')
        assert response.status_code == 404, f'Status code expected {404} but got {response.status_code}'
