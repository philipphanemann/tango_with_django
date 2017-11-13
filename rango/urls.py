from django.conf.urls import url
from rango import views

urlpatterns = [

    url(r'^$', views.index2, name='index2'),
    url(r'^about', views.about, name='about'),
]
