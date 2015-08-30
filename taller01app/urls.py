from django.conf.urls import url
from taller01app import views

urlpatterns = [
    url(r'^$', views.index), 
    url(r'^rest/departments/$', views.list_departments), 	
 	url(r'^rest/teachers/$', views.list_teachers),  	
 	url(r'^teachers/main$', views.show_teachers_main),
	url(r'^teachers/list$', views.show_teachers_list),

 	url(r'^rest/news/all$', views.list_all_news),
	url(r'^rest/news/filter$', views.find_news),
	url(r'^news/main$', views.show_news_main),
	url(r'^news/filter$', views.show_filtered_news),
	url(r'^news/all$', views.show_all_news),
]