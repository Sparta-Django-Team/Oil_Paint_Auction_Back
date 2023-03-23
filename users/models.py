# time
import time
import logging

# django
from django.db import models
from django.db import transaction, DatabaseError
from django.db.models import F
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

# project
from project_back.exceptions import AttendanceCheckException

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
POINT_INCREMENT = 1000

class UserManager(BaseUserManager):
    def create_user(self, email, nickname, password=None):
        if not email or not nickname:
            raise ValueError("이메일 또는 닉네임을 작성해주세요.")

        user = self.model(
            email=self.normalize_email(email),
            nickname=nickname,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, password=None):
        user = self.create_user(
            email=email,
            nickname=nickname,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField("이메일", max_length=100, unique=True)
    nickname = models.CharField("닉네임", max_length=10, unique=True)
    profile_image = models.ImageField("프로필 사진", default="default_profile_pic.jpg", upload_to="profile_pics")
    is_admin = models.BooleanField("어드민", default=False)
    point = models.PositiveIntegerField("포인트", default=10000)
    is_attendance_check = models.BooleanField("출석체크 여부", default=False)
    attendance_check_version = models.IntegerField("출석체크 버전", default=1)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nickname"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def update_attendance_check(self):
        # 포인트 증가 및 출석체크 여부 업데이트, 버전 증가
        updated_rows = User.objects.filter(
            id=self.id, attendance_check_version=self.attendance_check_version
        ).update(
            point=F("point") + POINT_INCREMENT,
            is_attendance_check=True,
            attendance_check_version=F("attendance_check_version") + 1,
        )
        return updated_rows == 1

    def process_attendance_check(self):
        if self.is_attendance_check:
            raise AttendanceCheckException("이미 출석체크를 하셨습니다.")

        retries = 0
        while retries < MAX_RETRIES:
            try:
                with transaction.atomic():
                    # 업데이트 성공한 경우 인스턴스 정보를 새로 고침
                    if self.update_attendance_check():
                        self.refresh_from_db()
                        return True

            # 충돌 & 데이터베이스 에러가 발생한 경우 잠시 대기후 재시도
            except DatabaseError:
                logger.exception("출석체크 업데이트 중 데이터베이스 에러가 발생했습니다.")
                pass

            time.sleep(0.5)
            retries += 1

        raise AttendanceCheckException("출석체크 업데이트 실패. 다시 시도해주시길 바랍니다.")
