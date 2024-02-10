from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
import json


class WeatherViewTests(TestCase):
    # Тест успешного получения данных о погоде
    @patch('requests.get')
    def test_weather_view_success(self, mock_get):
        # Настройка мока для имитации успешного ответа от API погоды
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "fact": {"temp": 20, "pressure_mm": 750, "wind_speed": 3}
        }

        # Создаем URL для теста и отправляем GET запрос
        url = reverse('weather_view') + '?city=Москва'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        # Проверяем содержание ответа
        content = json.loads(response.content)
        self.assertEqual(content['temperature'], 20)
        self.assertEqual(content['pressure'], 750)
        self.assertEqual(content['wind_speed'], 3)

    # Тест на ошибку при отсутствии города в запросе
    def test_weather_view_no_city_error(self):
        url = reverse('weather_view')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)

    # Тест проверки отсутствия города в базе
    def test_city_not_found(self):
        url = reverse('weather_view')
        response = self.client.get(url, {'city': 'faketown'})

        self.assertEqual(response.status_code, 404)
