from django.conf.urls import url
from taller01app import views

urlpatterns = [
    url(r'^departments/$', views.list_departments),
 	url(r'^teachers/$', views.list_teachers),   
]