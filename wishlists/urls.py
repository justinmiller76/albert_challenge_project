from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^add', views.add, name='add'),
    url(r'^remove', views.remove, name='remove'),
    url(r'^list_all', views.list_all, name='list_all')
]
