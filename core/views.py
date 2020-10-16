from django.views import generic as dviews

# Create your views here.
class Home(dviews.TemplateView):
    """ Home View """
    template_name = "core/home.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context