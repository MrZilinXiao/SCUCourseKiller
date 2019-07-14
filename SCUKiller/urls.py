from . import views
from django.conf.urls import url

app_name = 'SCUKiller'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.logIn, name="login"),
    url(r'^register/$', views.register, name="register"),
    url(r'^register/$', views.register, name="register"),
    url(r'^courseManagement/$', views.courseManagement, name="register"),
]
