import pytest
from model_bakery import baker

from client.models import Announcement

pytestmark = pytest.mark.django_db


class TestAnnouncement:
    img_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAADAFBMVEVHcEyqGi2yHzOrGy6lFiiZESCZESClFyikFiikFiiqGSyaESCbESCiEiKYESCgEiKlFiilFyikFiikFyihFSarGy6rGy6aESCaESCmFyiWER+iFSeWEB+aESGoGCqXEB+sGy6iFCSsGy6rGi2YESCmFSavHjKoGSufEyOfEySZESCaESCZESCmFSalFCabESGfEiOaESCYESCqGiykFCanGCqoGSypGiysGy6rGy6sGi2uHDCvGy+xHzOvHjGpGCudEiKsGy6lFSaoFiihEySVEB+bESGaESCdEyOfEyOVEB+sGSyoFymnGSurHC6mFiitHTCtHTCjFCSo/zH///+0GS22Gi61GS3AJDy/Ijq1Gi6zGSy4GzC8HTO/Izu6HDHBJT7AIzy9HzWyGCvAJD20GSzBJj65HDHBJT3AJT2+IDi5GzC+ITmwFyq8HjS3Gy+6HDK9Hza7HTKtFie9HjS3Gi+7HDK+IzvBJj+vFym7HTO+JDy7Ijm2Gi++IzqxFyuuFii+IDavFim5HzTAIzv57e7AJT6xFyqzGCy9IDi/JTy/JDyrFCbAJj26HzW4HzWsFieqFCW5GzGsFSe7ITi4HjO9HjW8IzqzGCu4Izi5IDa+Ijq4HDCoEyS0ITK7HzW7HjO9Ijm2HjO0Gi2/ITm4HDK8HzW3ITapFCWwFym2HTLtv8a5HTO3HzS8ITiyGSuzGS2xGCq6HjO7IDanEyTnr7e6HTK/JDulEyPbipW3HDC5JTq1HDC1ITa8IDbMUmP+/v6vFyrJUGC9IDa6ITi0Gy/FQVPLUWLcipa7IDegEiGxGy+1Gy/di5f89fa3GjC4Gi/Wd4T02d3SaXj9+fnHSFn+/f368PHTbn3AJTzKTV/34+XBLkPDNUnNVGXPXW3bg5DuyM778vThm6XekJu/KD345+rx0NT++/zquL++Kj7joqv13eHkpq746uzQZHLmqrPZfovuxMrflJ/y1dnosrnEOk3bh5PwzdG2GzDdjJjNWWm8JzvptLvdjJeyEQBbdlmRAAABAHRSTlMARP2PAslEBQgYIdn8/of6AQsNHltBKiLxkJFVtLPJjsnX2NPT/vBMj2xDKU358d/wK+Wz5rSght+02vP5+eWpqcPD78PDS0Gg5KD85IiI1Uts8OT////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////9XHoRqgAADy9JREFUeNq8mnlQU9cexy+EceGPvlqrbxxnHIEB8Q+dzmhdi9ZlOu3YfcJiCOE9Qk3ZLX08SiSEwlPACFrEPgOZES5PKFcSkSoMkKAlBmFAFgEFhII7bnVfqE/nnXPuTUzulgvE9/3DMfd37vl98lvOOfcGDJuEPDy//Eq0foP3Or8Ad/cAv3XeG9aLvvrS0wP7f2jmfNEGP5NJC1QOpNfDf+Enk8lvg2j+zDfqfIabyMcdetbjeqi9lNAHXA853H1EbjPejPfpbiv8wBcvx5HjQoYQCA4gTH4r3Ka73L3nynWmBi361tDbaaBUO8HPJAUYom0wrVvp6Urvb89ZHdDQAL2TvqHLf9NEYUAIMLChIWD1nLdd5N5j0UL05fdanUN/yQxRFAhiLwrDwkUu6Qs34L4cRt7qHHrbwSKKAkHAXJQDBLcpu5+7GrkvRO6Rc+Rst1W7dtn+a6WADGQYAMLquVNyP+vzAMp9QQEVeOQ7KioqlyZwCVFQySgooBACPp81heiv0WpJ91Tsd2g0msgoqL8xhC5HggE7qEyQCFrtmsnmYYbInax8EH3kHUiDos4tYNaQmQAIsBRgR7iLJrU0zfXRanEH9xp75z/QZA+hcUDAtVqfSVTCu2sbyM5juv+BUywIqCcb1r470XVX5I46H5Y+dC/EO5MBIICGQKuCu2hCq/M7y0xk+Cn/qO6jcndtE6RdsCWiYF/aCHCtadk7E9hyF2pR8xUUoPhrSPe52wQrl0TQoCwUFKCG1C4UvFXP9kbpPz1Z90wElIYG79kCN75VWj2+t7C1wFAC/WsiI1n73pngqgCWBUBQYihoLdyL67WrBG2Rs1dpcRx9/xLSfeRk3JMIkSRCCYoBjmtXCYjBTG/Sf6rV/2TdWxFIglSSwNtpHbyzAMY/rxV8/7TkWk1IyEDUt1NQ1EBIiKY2OQ3EoDUPZmGBk16Y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"

    @pytest.mark.parametrize("payload,expected_status",
                             [
                                 ({
                                      "images": [
                                          {
                                              "order": 1,
                                              "image": img_b64
                                          },
                                          {
                                              "order": 2,
                                              "image": img_b64
                                          },
                                          {
                                              "order": 3,
                                              "image": img_b64
                                          },
                                      ],
                                      "main_photo": img_b64,
                                      "address": "specific address",
                                      "map_lat": "38.8951",
                                      "map_lon": "-77.0364",
                                      "description": "string",
                                      "grounds_doc": "Собственность",
                                      "appointment": "Дом",
                                      "room_count": "1",
                                      "layout": "Студия, санузел",
                                      "living_condition": "Черновая",
                                      "kitchen_square": 50,
                                      "balcony_or_loggia": True,
                                      "heating_type": "Центральное",
                                      "payment_type": "Ипотека",
                                      "agent_commission": 5000,
                                      "communication_type": "Звонок + сообщение",
                                      "square": 150,
                                      "price": 100_000,
                                  }, 200),
                                 ({
                                      "main_photo": img_b64,
                                      "address": "specific address",
                                      "map_lat": "38.8951",
                                      "map_lon": "-77.0364",
                                      "description": "string",
                                      "grounds_doc": "Собственность",
                                      "appointment": "Дом",
                                      "room_count": "1",
                                      "layout": "Студия, санузел",
                                      "living_condition": "Черновая",
                                      "kitchen_square": 100,
                                      "balcony_or_loggia": True,
                                      "heating_type": "Центральное",
                                      "payment_type": "Ипотека",
                                      "agent_commission": 5000,
                                      "communication_type": "Звонок + сообщение",
                                      "square": 300,
                                      "price": 200_000,
                                  }, 200),
                                 ({
                                      "images": [
                                          {
                                              "order": 5,
                                              "image": img_b64
                                          },
                                          {
                                              "order": 10,
                                              "image": img_b64
                                          },

                                      ],
                                      "main_photo": img_b64,
                                      "address": "specific address",
                                      "map_lat": "38.8951",
                                      "map_lon": "-77.0364",
                                      "description": "string",
                                      "grounds_doc": "Собственность",
                                      "appointment": "Дом",
                                      "room_count": "1",
                                      "layout": "Студия, санузел",
                                      "living_condition": "Черновая",
                                      "kitchen_square": 150,
                                      "balcony_or_loggia": False,
                                      "heating_type": "Центральное",
                                      "payment_type": "Ипотека",
                                      "agent_commission": 5000,
                                      "communication_type": "Звонок + сообщение",
                                      "square": 100,
                                      "price": 100_000,
                                  }, 400),
                             ]
                             )
    def test_create_announcement(self, payload, expected_status, client):
        client_api, client = client
        response = client_api.post('/api/v1/client/announcements/', payload, format='json')
        assert response.status_code == expected_status, f'Status code expected {expected_status} but got {response.status_code}'

    @pytest.mark.parametrize("payload,expected_status",
                             [
                                 ({
                                      "images": [
                                          {
                                              "id": 1,
                                              "order": 1,
                                              "image": img_b64
                                          },
                                          {
                                              "id": 2,
                                              "order": 2,
                                              "image": img_b64
                                          },
                                          {
                                              "id": 3,
                                              "order": 3,
                                              "image": img_b64
                                          },
                                      ],
                                      "main_photo": img_b64,
                                      "address": "specific address",
                                      "map_lat": "38.8951",
                                      "map_lon": "-77.0364",
                                      "description": "string",
                                      "grounds_doc": "Собственность",
                                      "appointment": "Дом",
                                      "room_count": "1",
                                      "layout": "Студия, санузел",
                                      "living_condition": "Черновая",
                                      "kitchen_square": 50,
                                      "balcony_or_loggia": True,
                                      "heating_type": "Центральное",
                                      "payment_type": "Ипотека",
                                      "agent_commission": 5000,
                                      "communication_type": "Звонок + сообщение",
                                      "square": 150,
                                      "price": 100_000,
                                  }, 200),
                             ]
                             )
    def test_partial_update_announcement(self, payload, expected_status, client):
        client_api, client = client
        response = client_api.post('/api/v1/client/announcements/', payload, format='json')
        data_for_update = {
            "images": [
                {
                    "id": 1,
                    "order": 2
                },
                {
                    "id": 2,
                    "order": 1
                },
                {
                    "id": 5,
                    "order": 5,
                    "image": self.img_b64

                },
                {
                    "id": 6,
                    "order": 6,
                    "image": self.img_b64

                }
            ],
        }
        response = client_api.patch(f'/api/v1/client/announcements/{response.data["id"]}/', data_for_update,
                                    format='json')
        assert response.status_code == expected_status, f'Status code expected {expected_status} but got {response.status_code}'

    def test_switch_announcement_favorite(self, client):
        client_api, client = client
        obj = baker.make(Announcement)
        response = client_api.patch(f'/api/v1/client/announcements/{obj.id}/switch_announcement_favorite/',
                                    format='json')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        assert response.data == "Успешно добавлен", "Add announcement to favorite doesn't work"
        response = client_api.patch(f'/api/v1/client/announcements/{obj.id}/switch_announcement_favorite/',
                                    format='json')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        assert response.data == "Успешно удалён", "Remove announcement from favorite doesn't work"

    def test_delete_announcement(self, client):
        client_api, client = client
        obj = baker.make(Announcement, client_id=client.id)
        response = client_api.delete(f'/api/v1/client/announcements/{obj.id}/',
                                     format='json')
        assert response.status_code == 204, f'Status code expected {204} but got {response.status_code}'
        response = client_api.delete(f'/api/v1/client/announcements/{obj.id}/', format='json')
        assert response.status_code == 404, f'Status code expected {404} but got {response.status_code}'

    def test_get_announcements(self, client):
        client_api, client = client
        baker.make(Announcement, _quantity=10)
        response = client_api.get(f'/api/v1/client/announcements/',
                                  format='json')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        assert len(response.data) == 10, f'Announcements count expected {10} but got {len(response.data)}'

    def test_my_announcement(self, client):
        client_api, client = client
        baker.make(Announcement, client_id=client.id, _quantity=10)
        response = client_api.get(f'/api/v1/client/announcements/my_announcements/',
                                  format='json')
        assert response.status_code == 200, f'Status code expected {200} but got {response.status_code}'
        assert len(response.data) == 10, f'Announcements count expected {10} but got {len(response.data)}'
