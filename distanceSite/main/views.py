from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import loader
from .Helper_Functions import *


def login_request(request):
    if 'logintoken' in request.session.keys():
        if request.session['logintoken'] is not None:
            return redirect('/home')
    question, answer = get_question()
    context = {'question': question, 'answer': answer}
    template = loader.get_template("main/login.html")
    return HttpResponse(template.render(context, request))
