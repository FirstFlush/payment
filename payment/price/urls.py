from django.urls import path
from . import views

urlpatterns = [
    # path(''bleh/, views.bleh, name='bleh'),
    path('price/', views.get_price_test, name='get_price_test'),
    path('failure/', views.PriceApiFailureView.as_view(), name='price_api_failures'),
    path('current/', views.CurrentPriceView.as_view(), name='current_price'),
]