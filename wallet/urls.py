from django.urls import path
from . import views

urlpatterns = [
    # path(''bleh/, views.bleh, name='bleh'),
    path('notify/', views.notification, name='notification')
]