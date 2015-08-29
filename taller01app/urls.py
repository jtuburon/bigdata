from django.conf.urls import url
from taller01app import views

urlpatterns = [
    url(r'^$', views.index), 
    url(r'^rest/departments/$', views.list_departments),
 	url(r'^rest/teachers/$', views.list_teachers),  	
 	url(r'^teachers/$', views.show_teachers), 
]