from django.urls import path, include
from . import views
from rest_framework.authtoken import views as auth_views

urlpatterns = [
    # path(''bleh/, views.bleh, name='bleh'),
    path('notification/', views.notification, name='notification'),
    path('notify/', views.NotifyView.as_view(), name='notify'),
    # path('vendor_test/', views.vendor_request_test, name='vendor'),
    path('pay_request/', views.PayRequestView.as_view()),
    # path('thing/', include('knox.urls')),
    # path('api-token-auth/', auth_views.obtain_auth_token),
    
]