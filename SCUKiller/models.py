import datetime

from django.db import models

# Create your models here.
from django.contrib.auth.models import User


class UserProfile(models.Model):
    uid = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='UserProfile', unique=True)
    is_active = models.BooleanField('是否激活', default=False)
    telephone = models.CharField('电话', max_length=11, blank=True)
    regTime = models.DateTimeField('注册时间', auto_now_add=True)
    points = models.FloatField('点数', default=10.0)
    courseCnt = models.IntegerField('已添加课程数目', default=0)
    courseRemainingCnt = models.IntegerField('剩余课程权限', default=0)

    # 剩余抢课权限

    class Meta:
        verbose_name = '用户个人信息'


class jwcAccount(models.Model):
    jwcNumber = models.CharField('学号', max_length=100)
    jwcPasswd = models.CharField('密码', max_length=256)
    jwcCookie = models.CharField('Cookie', max_length=256)
    proxy = models.CharField('代理IP', max_length=100, default='')
    userprofile = models.OneToOneField(UserProfile, primary_key=True,
                                       on_delete=models.DO_NOTHING)  # 不加默认值在2.18中报错？ 之前的migrations没删

    class Meta:
        verbose_name = '教务处账号信息'

    def __str__(self):
        return self.jwcNumber


class EmailVerifyRecord(models.Model):
    # 验证码
    code = models.CharField(max_length=20, verbose_name=u"验证码")
    email = models.EmailField(max_length=50, verbose_name=u"邮箱")
    # 包含注册验证和找回验证
    send_type = models.CharField(verbose_name=u"验证码类型", max_length=10,
                                 choices=(("register", u"注册"), ("forget", u"找回密码")))
    send_time = models.DateTimeField(verbose_name=u"发送时间", default=datetime.datetime.now)

    class Meta:
        verbose_name = u"邮箱验证码"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return '{0}({1})'.format(self.code, self.email)


class courses(models.Model):
    cid = models.AutoField(primary_key=True)
    host = models.ForeignKey(UserProfile, related_name='coursesHost', on_delete=models.DO_NOTHING)
    status = models.CharField(verbose_name='状态', max_length=100, default='等待中')
    # 等待中 运行中 已完成 出错
    inq = models.BooleanField(verbose_name='正在队列中', default=False)
    keyword = models.CharField(verbose_name='关键词', max_length=50, default='')
    kcm = models.CharField(verbose_name='课程名', max_length=100, default='')
    kch = models.CharField(verbose_name='课程号', max_length=100, default='')
    kxh = models.CharField(verbose_name='课序号', max_length=100, default='')
    type = models.CharField(verbose_name='课程类型', max_length=10, default='自由选课')
    term = models.CharField(verbose_name='学期', max_length=100, default='2019-2020-1-1')
    teacher = models.TextField(verbose_name='授课老师', max_length=1000, default='')
    campus = models.CharField(verbose_name='校区', max_length=100, default='')
    location = models.CharField(verbose_name='上课地点', max_length=100, default='')
    addTime = models.DateTimeField('添加时间', auto_now_add=True)
    attempts = models.IntegerField(verbose_name="尝试次数", default=0)
    isSuccess = models.IntegerField(verbose_name='是否成功', default=0)  # -1 异常 0 未成功 1 已成功
    gid = models.CharField(verbose_name="组编号", default='', max_length=100)
    latestRemaining = models.IntegerField(verbose_name="最新剩余课余量", default=0)

    class Meta:
        verbose_name = "课程信息"


class notification(models.Model):
    host = models.ForeignKey(User, related_name='notificationHost', on_delete=models.DO_NOTHING)
    title = models.CharField('通知标题', max_length=100)
    content = models.TextField('通知内容')
    notiTime = models.DateTimeField('通知时间', auto_now_add=True)
    isRead = models.BooleanField('是否阅读', default=False)

    class Meta:
        verbose_name = "通知"


class codes(models.Model):
    code = models.CharField('神秘代码', max_length=1000)
    points = models.FloatField('点数', default=10.0)
    usedBy = models.CharField('被谁使用', max_length=1000, default='')
    addBy = models.CharField('由谁加入', max_length=1000, default='')
    createTime = models.DateTimeField('添加时间', auto_now_add=True)
    usedTime = models.CharField('使用时间', max_length=1000)


class Orders(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='Orders')
    method = models.CharField('支付方式', max_length=100, default='')  # 支付宝 微信
    trade_no = models.CharField('商户单号', max_length=100, default='')
    platform_no = models.CharField('第三方平台单号', max_length=100, default='')
    payment_tool_no = models.CharField('用户支付工具单号', max_length=100, default='')
    body = models.CharField('订单标题', max_length=1000, default='')
    total_fee = models.FloatField('订单金额')  # 1.33 以元为单位
    addTime = models.DateTimeField('订单生成时间', auto_now_add=True)
    payTime = models.CharField('订单支付时间', max_length=1000)
    closedTime = models.CharField('订单关闭时间', max_length=1000)
    status = models.IntegerField('状态', default=0)  # 0--等待 -1--失败 1---成功


class GlobalConf(models.Model):
    isActive = models.BooleanField(default=True)
