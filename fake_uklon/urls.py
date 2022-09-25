from django.urls import path

from fake_uklon.views import Login

urlpatterns = [
    path("login/", Login.as_view()),
]
