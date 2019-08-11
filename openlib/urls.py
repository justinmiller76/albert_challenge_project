from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^detail$', views.detail, name='detail'),
    url(r'^search$', views.search, name='search'),
]
