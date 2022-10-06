from django.urls import path
from . import views

urlpatterns = [
    # path(''bleh/, views.bleh, name='bleh'),
    path('notify/', views.notification, name='notification'),
    path('price/', views.get_price_test, name='get_price_test'),
]