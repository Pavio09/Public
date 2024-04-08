from django.db import models

# Create your models here.

#TODO: add e.g. colors of points in db

class AmenityGroup(models.Model):
    group_amenity = models.CharField(max_length=200, unique=True)
    name_en = models.CharField(max_length=200)
    name_pl = models.CharField(max_length=200)

    def __str__(self):
        return self.group_amenity


class Amenity(models.Model):
    amenity_key = models.CharField(max_length=200, unique=True)
    group_amenity = models.ForeignKey(AmenityGroup, on_delete=models.SET_NULL, null=True)
    name_en = models.CharField(max_length=200)
    name_pl = models.CharField(max_length=200)
    color = models.CharField(max_length=20)

    def __str__(self):
        return self.amenity_key