from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse('Rango says hey there partner')
# Create your views here.


def index2(request):
    return HttpResponse('This is the rango page <br/> <a href="about/"> About</a>')


def about(request):
    return HttpResponse('Rango says here is the about page.  <a href=/rango/>Index</a>')
