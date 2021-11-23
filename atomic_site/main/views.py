from django.http import HttpResponse
from django.template import loader


def home(request):
    # This will redirect any user not logged in to the login page.
    context = {}
    template = loader.get_template("main/home.html")
    return HttpResponse(template.render(context, request))
