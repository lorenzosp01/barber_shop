from django.urls import path

from cognito_auth.views import TestView, LoginView

urlpatterns = [
    path('get-token', LoginView.as_view(), name='login'),
    path('', TestView.as_view(), name='test'),
]