from django.shortcuts import render
from django.views.generic import TemplateView

from scripts.driversrating import DriversRatingMixin


class DriversRatingView(DriversRatingMixin, TemplateView):
    template_name = 'app/drivers_rating.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['rating'] = self.get_rating()
        return context
