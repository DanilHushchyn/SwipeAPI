import pytest
pytestmark = pytest.mark.django_db


class TestSubscription:
    def test_switch_autorenewal_subscription(self, client):
        client_api, client = client

        response = client_api.patch(f'/api/v1/client/subscriptions/switch_autorenewal/', format='json')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        assert response.data == "Автопродление подписки выключено", "Auto renewal subscription switcher doesn't work"
        response = client_api.patch(f'/api/v1/client/subscriptions/switch_autorenewal/', format='json')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        assert response.data == "Автопродление подписки включено", "Auto renewal  subscription switcher doesn't work"

    def test_renewal_subscription(self, client):
        client_api, client = client
        response = client_api.patch(f'/api/v1/client/subscriptions/renewal/', format='json')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        assert response.data == "Подписка успешно продлена на месяц", "Manual renewal subscription doesn't work"

    def test_my_subscription(self, client):
        client_api, client = client
        response = client_api.get(f'/api/v1/client/subscriptions/my_subscription/', format='json')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        assert response.data['auto_renewal'] == client.subscription.auto_renewal,  \
            f" Field content expected {client['auto_renewal']} but got {response.data['auto_renewal']}"
        assert response.data['is_active'] == client.subscription.is_active,  \
            f" Field content expected {client['is_active']} but got {response.data['is_active']}"
