from django import forms
from .models import UserProfile, User
import re
from django.core.validators import RegexValidator


class RegForm(forms.Form):
    userName = forms.CharField(label='Username', max_length=100, error_messages={'required': '用户名不能为空'},
                               widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'placeholder': '用户名',
                                                             'autofocus': ''}))
    email = forms.EmailField(label='Email', max_length=100, error_messages={'required': '邮箱不能为空', 'invalid': "邮箱格式错误"},
                             widget=forms.TextInput(attrs={'class': 'form-control',
                                                           'placeholder': '电子邮箱'}))
    phoneNumber = forms.CharField(label='PhoneNumber', max_length=11,
                                  widget=forms.TextInput(attrs={'class': 'form-control',
                                                                'placeholder': '11位手机号',
                                                                'onkeyup': 'value=value.replace(/[^0-9]/g,'')'}))
    password = forms.CharField(label='Password', min_length=8, max_length=256,
                               widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                 'placeholder': '密码'}))
    passwordTwice = forms.CharField(label='PasswordTwice', max_length=256,
                                    widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                      'placeholder': '再次输入密码',
                                                                      'onblur': 'validate()'}))
    captcha = forms.CharField(label='Captcha', max_length=4, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                           'placeholder': '验证码'}))

    def clean(self):  # 检查除了验证码之外的注册信息
        try:
            username = self.cleaned_data['userName']
            email = self.cleaned_data['email']
        except Exception as e:
            print('except: ' + str(e))
            raise forms.ValidationError(u"用户名或邮箱不符合格式")

        is_username_exist = User.objects.filter(username=username).exists()
        is_email_exist = User.objects.filter(email=email).exists()
        if is_username_exist or is_email_exist:
            print('Already Taken')
            raise forms.ValidationError(u"用户名或邮箱已被注册")
        try:
            password = self.cleaned_data['password']
        except Exception as e:
            print('except: ' + str(e))
            raise forms.ValidationError(u"请输入至少8位密码")
        try:
            phonenumber = self.cleaned_data['phoneNumber']
            ret = re.match(r"^1[3456789]\d{9}$", phonenumber)
            if not ret:
                raise forms.ValidationError
        except Exception as e:
            print('except: ' + str(e))
            raise forms.ValidationError(u"手机号码格式不正确")
        return self.cleaned_data


class LoginForm(forms.Form):
    userName = forms.CharField(label='Username', max_length=100, error_messages={'required': '用户名不能为空'},
                               widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'placeholder': '用户名',
                                                             'autofocus': ''}))
    password = forms.CharField(label='Password', max_length=256,
                               widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                 'placeholder': '密码'}))
    captcha = forms.CharField(label='Captcha', max_length=4, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                           'placeholder': '验证码'}))

    def clean(self):
        try:
            username = self.cleaned_data['userName'].strip()
            password = self.cleaned_data['password']
        except Exception as e:
            print('Error when login: ' + str(e))
            raise forms.ValidationError(u"用户名或密码不符合格式")


class AddCourseForm(forms.Form):
    kch = forms.CharField(label='kch', max_length=9, validators=[RegexValidator(r'^[0-9]+$', '请输入数字')],
                          widget=forms.TextInput(attrs={'class': 'form-control',
                                                        'placeholder': '请输入9位课程号，只启用关键词选课可留空'}))
    kxh = forms.CharField(label='kxh', max_length=3, validators=[RegexValidator(r'^[0-9]+$', '请输入数字')],
                          widget=forms.TextInput(attrs={'class': 'form-control',
                                                        'placeholder': '请输入课序号，只启用关键词选课可留空'}))
    keyword = forms.CharField(label='keyword', max_length=100,
                              widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': '请输入课程关键词，留空代表仅监控指定课程',
                                                            'autofocus': ''}))
    type = forms.fields.ChoiceField(
        choices=((1, "自由选课"), (2, "方案选课")),
        label="课程类型",
        initial=1,
        widget=forms.widgets.RadioSelect
    )


class AddjwcAccount(forms.Form):
    stuID = forms.CharField(label='stuID', max_length=13, error_messages={'required': '学号不能为空'},
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': '请输入13位学号'}))
    stuPass = forms.CharField(label='Password', max_length=256,
                              widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                'placeholder': '密码'}))

    # def __init__(self, username):
    #     super().__init__()
    #     self.username = username
    #
    # def clean(self):
    #     try:
    #         stuID = self.cleaned_data["stuID"].strip()
    #         stuPass = self.cleaned_data["stuPass"].strip()
    #         if len(stuID) != 13:
    #             raise forms.ValidationError(u"学号不满足13位长度要求！")
    #         try:
    #             cookie = jwcAccount.valjwcAccount(stuID, stuPass)
    #             user = User.objects.get(username=self.username)
    #             jwc = jwcModel(jwcNumber=stuID, jwcPasswd=stuPass, jwcBelongto=user.UserProfile, jwcCookie=cookie)
    #             jwc.save()  # TODO: verify if this is working
    #         except Exception as e:
    #             print(e)
    #             raise forms.ValidationError(u"登录失败！")
    #     except Exception as e:
    #         print(e)
    #         raise forms.ValidationError(u"学号或密码格式出错！")
