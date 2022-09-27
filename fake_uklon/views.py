import logging

from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import mimetypes
import os
from django.http.response import HttpResponse


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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


class Export(LoginRequiredMixin, View):
    """Generate report"""

    login_url = '/fake_uklon/login/'
    redirect_field_name = '/fake_uklon/login/'
    # url = f"https://partner.uklon.com.ua/partner/export/fares?
    # page=1
    # &pageSize=20
    # &startDate={self.start_of_week_timestamp()}
    # &endDate={self.end_of_week_timestamp()}
    # &format=csv"

    @staticmethod
    def get(request):
        format_request = request.GET.get("format")
        if format_request == "csv":
            filename = 'Куцко - Income_9_12_2022 3_00_00 AM-9_19_2022 3_00_00 AM.csv'
            filepath = BASE_DIR + '/' + filename  # Define the full file path
            path = open(filepath, 'r')
            response = HttpResponse(path,
                                    content_type='text/csv',
                                    headers={'Content-Disposition': 'attachment; filename="Income_9_12_2022 3_00_00 AM-9_19_2022 3_00_00 AM.csv"'})
            return response
        return render(request, "fake_uklon/report.html")


