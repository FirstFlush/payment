from django.urls import path
from . import views

urlpatterns = [
    # path(''bleh/, views.bleh, name='bleh'),
    path('get_price/', views.get_price, name='get_price')
]