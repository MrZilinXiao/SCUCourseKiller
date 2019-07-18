from . import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # User Management Module
    url(r'^login/$', views.logIn, name="login"),
    url(r'^logout/$', views.logOut, name="logout"),
    url(r'^register/$', views.register, name="register"),
    url(r'^notification/$', views.notification, name="notification"),
    # url(r'^courseManagement/$', views.courseManagement, name="courseManagement"),
    # url(r'^accountManagement/$', views.accountManagement, name="accountManagement"),


    url(r'^check_captcha', views.check_captcha, name="check_captcha"),
    url(r'^checkUsername', views.checkUsername, name="checkUsername"),

]
