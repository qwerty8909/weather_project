from django.db import models


class Weather(models.Model):
    city = models.CharField(max_length=100)
    temperature = models.FloatField()
    pressure = models.IntegerField()
    wind_speed = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)
