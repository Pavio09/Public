from django.contrib import admin

# Register your models here.

from .models import Amenity, AmenityGroup

admin.site.register(Amenity)
admin.site.register(AmenityGroup)