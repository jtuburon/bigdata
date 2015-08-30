from django.conf.urls import url
from taller01app import views

urlpatterns = [
    url(r'^$', views.index), 
    url(r'^rest/departments/$', views.list_departments), 	
 	url(r'^rest/teachers/$', views.list_teachers),  	
 	url(r'^teachers/$', views.show_teachers),

 	url(r'^rest/news/all$', views.list_all_news),
	url(r'^rest/news/filter$', views.find_news),
]