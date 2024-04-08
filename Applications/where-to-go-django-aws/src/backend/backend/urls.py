from django.urls import path
from . import views

urlpatterns = [
    path('', views.map_view, name='map'),
    path('calculate-area/', views.calculate_area),
    path('generate-route/', views.generate_route)
]
