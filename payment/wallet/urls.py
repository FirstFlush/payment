from django.urls import path, include
from . import views
from rest_framework.authtoken import views as auth_views

urlpatterns = [
    path('notify/', views.NotifyView.as_view(), name='notify'),
    path('pay_request/', views.PayRequestView.as_view(), name='pay_request'),
    path('test/', views.TestView.as_view(), name='test'),
    path('serial/', views.SerializerTest.as_view(), name='serializer_test'),
    # path('thing/', include('knox.urls')),
    # path('api-token-auth/', auth_views.obtain_auth_token),
]