from django.db import models

from django.db import models

# Create your models here.
from django.contrib.auth.models import User


class UserProfile(models.Model):
    uid = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    telephone = models.CharField('Telephone', max_length=50, blank=True)
    regTime = models.DateTimeField('regTime', auto_now_add=True)
    courseCnt = models.IntegerField('courseCnt', default=0)

    # 剩余抢课权限

    class Meta:
        verbose_name = 'User Profile'

    def __str__(self):
        return self.user.__str__()


class jwcAccount(models.Model):
    jwcNumber = models.TextField('jwcNumber')
    jwcPasswd = models.TextField('jwcPasswd')
    jwcCookie = models.TextField('jwcCookie')
    jwcBelongto = models.OneToOneField("UserProfile", to_field="uid", on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'jwcAccount'

    def __str__(self):
        return self.jwcNumber


class coursesWatching(models.Model):
    host = models.ForeignKey(UserProfile, related_name='coursesHost', on_delete=models.CASCADE)
    courseName = models.CharField(verbose_name='courseName', max_length=100, default='')
    kch = models.CharField(verbose_name='kch', max_length=100, default='')
    kxh = models.CharField(verbose_name='kxh', max_length=100, default='')
    startTime = models.DateTimeField('startTime', auto_now_add=True)
    attempts = models.IntegerField(verbose_name="attempts", default=0)
    isSuccess = models.BooleanField(verbose_name='isSuccess', default=False)

    class Meta:
        verbose_name = "coursesWatching"


