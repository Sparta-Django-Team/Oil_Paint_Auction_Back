from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, nickname, password=None):
        if not email:
            raise ValueError('이메일을 작성해주세요')

        user = self.model(
            email=self.normalize_email(email),
            nickname=nickname,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, password=None):
        user = self.create_user(
            email,
            password=password,
            nickname=nickname,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    
    STATUS_CHOICES = (
        ('N', 'user_normal'), #정상
        ('S', 'user_stop'), #로그인 횟수 제한 -> 계정 잠금
        ('W', 'user_withdrawal'), #비활성화
        ('AW', 'admin_withdrawal'), #관리자 비활성화
    )

    RETENTION_PERIOD_CHOICES = (
        (str(timezone.now().date() + timezone.timedelta(days=365)), '1year'),
    )
    
    email = models.EmailField('이메일', max_length=100, unique=True, error_messages={"unique": "이미 사용중인 이메일 이거나 탈퇴한 이메일 입니다."})
    nickname = models.CharField('닉네임', max_length=10, unique=True, error_messages={"unique":"이미 사용중인 닉네임 이거나 탈퇴한 닉네임 입니다."})
    profile_image = models.ImageField('프로필 사진', default='default_profile_pic.jpg', upload_to='profile_pics' )
    status = models.CharField('회원 상태',max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    is_admin = models.BooleanField('어드민', default=False)
    retention_period =models.TextField('회원정보 보유기간', choices=RETENTION_PERIOD_CHOICES, default=RETENTION_PERIOD_CHOICES[0][0])
    lock_count = models.IntegerField('로그인 제한 횟수', default=0)
    lock_time = models.DateTimeField('로그인 제한 시간',null=True)
    point = models.PositiveIntegerField('포인트', default=10000)
    today_point = models.BooleanField('오늘 포인트받은 여부',default=False)
    term_check = models.BooleanField('약관 동의 여부', null=True, default=False)
    
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.status
    
    