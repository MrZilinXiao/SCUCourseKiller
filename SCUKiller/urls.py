from . import views
from . import utils
from . import tasks
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^inner_index/$', views.inner_index, name='inner_index'),
    # User Management Module
    url(r'^login/$', views.logIn, name="login"),
    url(r'^logout/$', views.logOut, name="logout"),
    url(r'^register/$', views.register, name="register"),
    url(r'^active/(?P<active_code>.*)/$', views.ActiveUserView.as_view(), name="user_active"),
    url(r'^notification/$', views.notification, name="notification"),
    url(r'^courseManagement/$', views.courseManagement, name="courseManagement"),

    url(r'^topup$', views.topup, name="topup"),
    url(r'^addCodes$', views.addCodes, name="addCodes"),
    url(r'^getCodesList$', views.getCodesList, name="getCodesList"),
    url(r'^storeExchange$', views.storeExchange, name="storeExchange"),
    url(r'^addCourse$', views.addCourse, name="addCourse"),
    url(r'^jwcAccount$', views.jwcAccount, name="jwcAccount"),
    url(r'^deljwcAccount$', views.deljwcAccount, name="deljwcAccount"),
    url(r'^alterUserinfo$', views.alterUserinfo, name="alterUserinfo"),
    url(r'^delReadNotification$', views.delReadNotification, name="delReadNotification"),
    url(r'^delNotification$', views.delNotification, name="delNotification"),

    # url(r'^watcher', utils.watchCourses, name="watcher"),
    url(r'^check_captcha', views.check_captcha, name="check_captcha"),
    url(r'^checkUsername', views.checkUsername, name="checkUsername"),
    url(r'^checkCookie', views.checkCookie, name="checkCookie"),
    url(r'^getCourseList', views.getCourseList, name="getCourseList"),

    url(r'^wxpay', views.wxpay, name="wxpay"),
    url(r'^alipay', views.alipay, name="alipay"),
    url(r'^check_pay', views.check_pay, name="check_pay"),
    url(r'^cancel_order', views.cancel_order, name="cancel_order"),
    url(r'^paycat_callback', views.paycat_callback, name="pay_callback"),
    # url(r'^test/$', tasks.watchUserCourses, name='test'),
]

handler404 = views.page_not_found
handler500 = views.page_error
