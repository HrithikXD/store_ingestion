from django.db import models

class StoreBrand(models.Model):
    name = models.CharField(max_length=255, unique=True)

class StoreType(models.Model):
    name = models.CharField(max_length=255, unique=True)

class City(models.Model):
    name = models.CharField(max_length=255, unique=True)

class State(models.Model):
    name = models.CharField(max_length=255, unique=True)

class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)

class Region(models.Model):
    name = models.CharField(max_length=255, unique=True)


class Store(models.Model):
    store_id = models.CharField(max_length=255, unique=True)
    store_external_id = models.CharField(max_length=255, default='')
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    store_brand = models.ForeignKey(StoreBrand, null=True, on_delete=models.SET_NULL)
    store_type = models.ForeignKey(StoreType,null=True, on_delete=models.SET_NULL)
    city = models.ForeignKey(City,null=True, on_delete=models.SET_NULL)
    state = models.ForeignKey(State, null=True, on_delete=models.SET_NULL)
    country = models.ForeignKey(Country, null=True, on_delete=models.SET_NULL)
    region = models.ForeignKey(Region, null=True, on_delete=models.SET_NULL)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)


