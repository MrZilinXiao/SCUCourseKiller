from django import forms
from .models import UserProfile, User


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
            raise forms.ValidationError(u"用户名或密码不符合格式")

            # 登录验证
        is_username_exist = User.objects.filter(username=username).exists()
        is_email_exist = User.objects.filter(email=email).exists()
        if is_username_exist or is_email_exist:
            raise forms.ValidationError(u"用户名或邮箱已被注册")
        try:
            password = self.cleaned_data['password']
        except Exception as e:
            print('except: ' + str(e))
            raise forms.ValidationError(u"请输入至少8位密码")

        return self.cleaned_data
