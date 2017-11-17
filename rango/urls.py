from django.conf.urls import url
from rango import views

urlpatterns = [

    url(r'^$', views.index2, name='index2'),
    url(r'^about', views.about, name='about'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/$',
        views.show_category, name='show_category'),
]
