import logging

from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.views import View

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)


class Login(View):
    @staticmethod
    def get(request):
        return render(request, "fake_uklon/login.html")

    @staticmethod
    def post(request):
        user_login = request.POST.get("login")
        password = request.POST.get("password")
        user = authenticate(username=user_login, password=password)

        if user is not None:
            login(request, user)
            warning = f"Hello, {user}"
            return render(
                request, "fake_uklon/warning.html", context={"warning": warning}
            )
        else:
            warning = "Wrong login or password"
            return render(
                request, "fake_uklon/warning.html", context={"warning": warning}
            )
