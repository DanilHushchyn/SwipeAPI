import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from builder.models import Complex, Floor, Sewer, Section, Corp, Apartment
from client.models import Announcement

pytestmark = pytest.mark.django_db


class TestApartment:

    @pytest.mark.parametrize("payload,expected_status",
                             [
                                 (
                                         {
                                             "number": "1",
                                             "square": 150,
                                             "price": 50_000,
                                             "is_booked": False,
                                         }, 200
                                 ),
                                 (
                                         {
                                             "number": "2",
                                             "square": 150,
                                             "price": 50_000,
                                             "is_booked": True,
                                         }, 200
                                 ),
                             ]
                             )
    def test_create_apartment(self, payload, expected_status, builder):
        client_api, builder = builder
        complex = baker.make(Complex, builder=builder)
        corp = baker.make(Corp, complex_id=complex.id)
        section = baker.make(Section, corp_id=corp.id)
        payload["section"] = section.id
        payload["floor"] = baker.make(Floor, section_id=section.id).id
        payload["sewer"] = baker.make(Sewer, section_id=section.id).id
        response = client_api.post('/api/v1/builder/apartments/add_to_my_complex/', payload, format='multipart')
        assert response.status_code == expected_status, \
            f'Status code expected {expected_status} but got {response.status_code}'
        assert response.data['number'] == payload['number'], \
            f'Status code expected {payload["number"]} but got {response.data["number"]}'
        assert response.data['square'] == payload['square'], \
            f'Status code expected {payload["square"]} but got {response.data["square"]}'
        assert response.data['price'] == payload['price'], \
            f'Status code expected {payload["price"]} but got {response.data["price"]}'

    def test_switch_apartment_booking(self, builder):
        client_api, builder = builder
        apartment = baker.make(Apartment,owner=builder)
        response = client_api.patch(f'/api/v1/builder/apartments/{apartment.id}/switch_booking/',
                                    format='multipart')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        assert response.data == "Успешно забронировано", "Add apartment to booked doesn't work"
        response = client_api.patch(f'/api/v1/builder/apartments/{apartment.id}/switch_booking/',
                                    format='multipart')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        assert response.data == "Успешно снята бронь", "Remove apartment from booked doesn't work"

    def test_get_apartments_unmoderated_for_my_complex(self, builder):
        client_api, builder = builder
        complex = baker.make(Complex, builder=builder)
        baker.make(Apartment, complex_id=complex.id, is_moderated=None, _quantity=5)
        response = client_api.get(f'/api/v1/builder/apartments/unmoderated_for_my_complex/', format='multipart')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        assert len(response.data) == 5, f'Status code expected {5} but got {len(response.data)}'

    def test_retrieve_apartment(self, builder):
        client_api, builder = builder
        apartment = baker.make(Apartment)
        response = client_api.get(f'/api/v1/builder/apartments/{apartment.id}/', format='multipart')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'

    def test_delete_apartment(self, builder):
        client_api, builder = builder
        apartment = baker.make(Apartment)
        response = client_api.delete(f'/api/v1/builder/apartments/{apartment.id}/', format='multipart')
        assert response.status_code == 204, f'Status code expected {204} but got {response.status_code}'
