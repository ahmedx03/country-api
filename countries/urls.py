from django.urls import path
from . import views

urlpatterns = [
    path('countries/image', views.get_countries_image, name='countries-image'),
    path('countries/refresh', views.refresh_countries, name='refresh-countries'),
    path('countries', views.list_countries, name='list-countries'),
    path('countries/<str:name>', views.get_country_by_name, name='get-country'),
    path('countries/<str:name>/delete', views.delete_country, name='delete-country'),
    path('status', views.get_status, name='status'),
]