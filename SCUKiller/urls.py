from . import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^inner_index/$', views.inner_index, name='inner_index'),
    # User Management Module
    url(r'^login/$', views.logIn, name="login"),
    url(r'^logout/$', views.logOut, name="logout"),
    url(r'^register/$', views.register, name="register"),
    url(r'^notification/$', views.notification, name="notification"),
    url(r'^courseManagement/$', views.courseManagement, name="courseManagement"),
    url(r'^accountManagement/$', views.accountManagement, name="accountManagement"),


    url(r'^addCourse$', views.addCourse, name="addCourse"),
    url(r'^jwcAccount$', views.jwcAccount, name="jwcAccount"),
    url(r'^deljwcAccount$', views.deljwcAccount, name="deljwcAccount"),
    url(r'^alterUserinfo$', views.alterUserinfo, name="alterUserinfo"),
    url(r'^delReadNotification$', views.delReadNotification, name="delReadNotification"),


    url(r'^check_captcha', views.check_captcha, name="check_captcha"),
    url(r'^checkUsername', views.checkUsername, name="checkUsername"),
    url(r'^checkCookie', views.checkCookie, name="checkCookie"),

]
