# rest_framework
from rest_framework.test import APITestCase

# django
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator

# users
from users.models import User

# python
from PIL import Image
import tempfile


def get_temporary_image(temp_file):
    size = (200, 200)
    color = (255, 0, 0, 0)
    image = Image.new("RGBA", size, color)
    image.save(temp_file, "png")
    return temp_file

class AuthSignupAPIViewTestCase(APITestCase):
    
    # 회원가입 성공
    def test_signup_success(self):
        url = reverse("signup")
        user_data = {
            "email":"test@test.com",
            "nickname":"test",
            "password":"Test1234!",
            "repassword":"Test1234!",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 201)
    
    # 회원가입 실패(이메일 빈칸)
    def test_signup_email_blank_fail(self):
        url = reverse("signup")
        user_data = {
            "email":"",
            "nickname":"test",
            "password":"Test1234!",
            "repassword":"Test1234!",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
        
    # 회원가입 실패(이메일 형식)
    def test_signup_email_invalid_fail(self):
        url = reverse("signup")
        user_data = {
            "email":"test",
            "nickname":"test",
            "password":"Test1234!",
            "repassword":"Test1234!",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
        
    # 회원가입 실패(이메일 중복)
    def test_signup_email_unique_fail(self):
        User.objects.create_user("test@test.com","test","Test1234!")
        url = reverse("signup")
        user_data = {
            "email":"test@test.com",
            "nickname":"test1",
            "password":"Test1234!",
            "repassword":"Test1234!",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
        
    # 회원가입 실패(닉네임 빈칸)
    def test_signup_nickname_blank_fail(self):
        url = reverse("signup")
        user_data = {
            "email":"test@test.com",
            "nickname":"",
            "password":"Test1234!",
            "repassword":"Test1234!",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
        
    # 회원가입 실패(닉네임 유효성검사)
    def test_signup_nickname_validation_fail(self):
        url = reverse("signup")
        user_data = {
            "email":"test@test.com",
            "nickname":"n!",
            "password":"Test1234!",
            "repassword":"Test1234!",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
    
    # 회원가입 실패(닉네임 중복)
    def test_signup_nickname_unique_fail(self):
        User.objects.create_user("test@test.com","test","Test1234!")
        url = reverse("signup")
        user_data = {
            "email":"test1@test.com",
            "nickname":"test",
            "password":"Test1234!",
            "repassword":"Test1234!",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
    
    # 회원가입 실패(비밀번호 빈칸)
    def test_signup_password_blank_fail(self):
        url = reverse("signup")
        user_data = {
            "email":"test@test.com",
            "nickname":"test",
            "password":"",
            "repassword":"Test1234!",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
        
    # 회원가입 실패(비밀번호확인 빈칸)
    def test_signup_password_confirm_blank_fail(self):
        url = reverse("signup")
        user_data = {
            "email":"test@test.com",
            "nickname":"test",
            "password":"Test1234!",
            "repassword":"",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
        
    # 회원가입 실패(비밀번호, 비밀번호 확인 일치)
    def test_signup_password_same_fail(self):
        url = reverse("signup")
        user_data = {
            "email":"test@test.com",
            "nickname":"test",
            "password":"Test1234!",
            "repassword":"Test12345!",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
        
    # 회원가입 실패(비밀번호 유효성 검사(simple))
    def test_signup_password_validation_fail(self):
        url = reverse("signup")
        user_data = {
            "email":"test@test.com",
            "nickname":"test",
            "password":"t1",
            "repassword":"t1",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
        
    # 회원가입 실패(약관동의)
    def test_signup_term_checkt_fail(self):
        url = reverse("signup")
        user_data = {
            "email":"test@test.com",
            "nickname":"test",
            "password":"Test111!",
            "repassword":"Test111!",
            "term_check":"False",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)


class AuthLoginAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.success_data = {"email": "test@test.com", "password":"Test1234!"}
        self.fail_data = {"email": "test1@test.com", "password":"Test1234!!"}
        self.user = User.objects.create_user("test@test.com","test","Test1234!")
    
    def setUp(self):
        self.access_token = self.client.post(reverse("token_obtain_pair"), self.success_data).data["access"]
        self.refresh_token = self.client.post(reverse("token_obtain_pair"), self.success_data).data["refresh"]

    # 로그인 성공(access_token, refresh_token)
    def test_login_get_token_success(self):
        response = self.client.post(reverse('token_obtain_pair'), self.success_data)
        self.assertEqual(response.status_code, 200)
    
    # 로그인 실패(access_token, refresh_token)
    def test_login_get_token_fail(self):
        response = self.client.post(reverse('token_obtain_pair'), self.fail_data)
        self.assertEqual(response.status_code, 401)

    # 로그인 성공(refresh_token)
    def test_login_get_refresh_token_success(self):
        response = self.client.post(
            path=reverse("token_refresh"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"refresh": self.refresh_token},
        )
        self.assertEqual(response.status_code, 200)

    # 로그인 실패(refresh_token 잘못된 값)
    def test_login_get_refresh_token_fail(self):
        response = self.client.post(
            path=reverse("token_refresh"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"refresh": f"{self.refresh_token}1"},
        )
        self.assertEqual(response.status_code, 401)

    # 로그인 실패(refresh_token blank)
    def test_login_get_refresh_token_blank_fail_(self):
        response = self.client.post(
            path=reverse("token_refresh"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"refresh": ""},
        )
        self.assertEqual(response.status_code, 400)

    # 로그인 실패(refresh_token required)
    def test_login_get_refresh_token_required_fail_(self):
        response = self.client.post(
            path=reverse("token_refresh"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)


class AuthTokenVerifyAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.success_data = {"email": "test@test.com", "password":"Test1234!"}
        self.fail_data = {"email": "test1@test.com", "password":"Test1234!!"}
        self.user = User.objects.create_user("test@test.com","test","Test1234!")
    
    def setUp(self):
        self.access_token = self.client.post(reverse("token_obtain_pair"), self.success_data).data["access"]
        self.refresh_token = self.client.post(reverse("token_obtain_pair"), self.success_data).data["refresh"]

    # access_token verify success
    def test_access_token_verify_success(self):
        response = self.client.post(
            path=reverse("token_verify"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"token": self.access_token},
        )
        self.assertEqual(response.status_code, 200)

    # refresh_token verify success
    def test_refresh_token_verify_success(self):
        response = self.client.post(
            path=reverse("token_verify"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"token": self.refresh_token},
        )
        self.assertEqual(response.status_code, 200)

    # token verify invalid
    def test_token_verify_fail(self):
        response = self.client.post(
            path=reverse("token_verify"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"token": f"{self.access_token}123"},
        )
        self.assertEqual(response.status_code, 401)


class AuthLogoutAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.success_data = {"email": "test@test.com", "password":"Test1234!"}
        self.fail_data = {"email": "test1@test.com", "password":"Test1234!!"}
        self.user = User.objects.create_user("test@test.com","test","Test1234!")
    
    def setUp(self):
        self.access_token = self.client.post(reverse("token_obtain_pair"), self.success_data).data["access"]
        self.refresh_token = self.client.post(reverse("token_obtain_pair"), self.success_data).data["refresh"]
    
    # 로그아웃 성공
    def test_logout_success(self):
        response = self.client.post(
            path=reverse("logout"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"refresh": self.refresh_token},
        )
        self.assertEqual(response.status_code, 200)

    # 로그아웃 실패(refresh required)
    def test_logout_required_fail(self):
        response = self.client.post(
            path=reverse("logout"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)

    # 로그아웃 실패(refresh required)
    def test_logout_blank_fail(self):
        response = self.client.post(
            path=reverse("logout"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"refresh": ""},
        )
        self.assertEqual(response.status_code, 400)

    # 로그아웃 실패(access token)
    def test_logout_invalid_fail(self):
        response = self.client.post(
            path=reverse("logout"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"refresh": self.access_token},
        )
        self.assertEqual(response.status_code, 400)


class PasswordChangeAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.user_data = {"email": "test@test.com", "password":"Test1234!"}
        self.user = User.objects.create_user("test@test.com","test","Test1234!")
    
    def setUp(self):
        self.access_token = self.client.post(reverse("token_obtain_pair"), self.user_data).data["access"]
    
    # 비밀번호 변경 성공
    def test_password_change_success(self):
        response = self.client.put(
            path=reverse("password_change"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"password":"Test1234!!!", "repassword":"Test1234!!!"} 
        )
        self.assertEqual(response.status_code, 200)
    
    # 비밀번호 변경 실패(비밀번호 빈칸)
    def test_password_change_password_blank_fail(self):
        response = self.client.put(
            path=reverse("password_change"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"password":"", "repassword":"Test1234!!"} 
        )
        self.assertEqual(response.status_code, 400)

    # 비밀번호 변경 실패(비밀번호 확인 빈칸)
    def test_password_change_password_confirm_blank_fail(self):
        response = self.client.put(
            path=reverse("password_change"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"password":"Test1234!!", "repassword":""} 
        )
        self.assertEqual(response.status_code, 400)
        
    # 비밀번호 변경 실패(비밀번호 현재비밀번호와 동일시)
    def test_password_change_current_password_same_fail(self):
        response = self.client.put(
            path=reverse("password_change"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"password":"Test1234!", "repassword":"Test1234!"} 
        )
        self.assertEqual(response.status_code, 400)
        
    # 비밀번호 변경 실패(비밀번호 유효성검사(simple))
    def test_password_change_password_validation_fail(self):
        response = self.client.put(
            path=reverse("password_change"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"password":"Test1234", "repassword":"Test1234"} 
        )
        self.assertEqual(response.status_code, 400)
    
    # 비밀번호 변경 실패(비밀번호, 비밀번호 확인 일치)
    def test_password_change_password_same_fail(self):
        response = self.client.put(
            path=reverse("password_change"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"password":"Test1234!!", "repassword":"Test1234!"} 
        )
        self.assertEqual(response.status_code, 400)


class PasswordResetAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(self):
        User.objects.create_user("test1@test.com","test","Test1234!")

    # 비밀번호 찾기 이메일 전송 성공
    def test_password_reset_email_success(self):
        response = self.client.post(
            path=reverse("password_reset"), 
            data={"email": "test1@test.com"},
        )
        print(response.data)
        self.assertEqual(response.status_code, 200)

    # 존재하지 않는 이메일전송
    def test_password_reset_email_fail(self):
        response = self.client.post(
            path=reverse("password_reset"), 
            data={"email": "test2@test.com"},
        )
        self.assertEqual(response.status_code, 400)

    # 형식에 맞지 않는 이메일전송
    def test_password_reset_email_invalid_fail(self):
        response = self.client.post(
            path=reverse("password_reset"), 
            data={"email": "test2"},
        )
        self.assertEqual(response.status_code, 400)

    # 이메일 빈칸일 때 이메일 전송
    def test_password_reset_email_blank_fail(self):
        response = self.client.post(
            path=reverse("password_reset"), 
            data={"email": ""},
        )
        self.assertEqual(response.status_code, 400)


class PasswordTokenCheckAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.user = User.objects.create_user("test1@test.com","test","Test1234!")
        self.uidb64 = urlsafe_base64_encode(smart_bytes(self.user.id))
        self.token = PasswordResetTokenGenerator().make_token(self.user)

    # 비밀번호 토큰 인증 성공
    def test_password_token_check_success(self):
        response = self.client.get(
            path=reverse("password_reset_confirm",
            kwargs={"uidb64": self.uidb64, "token": self.token},),
        )
        self.assertEqual(response.status_code, 200)

    # 비밀번호 토큰 인증 실패
    def test_password_token_check_fail(self):
        response = self.client.get(
            path=reverse("password_reset_confirm", 
            kwargs={"uidb64": "11", "token": "11"})
        )
        self.assertEqual(response.status_code, 401)


class SetPasswordAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.user = User.objects.create_user("test1@test.com","test","Test1234!")
        self.uidb64 = urlsafe_base64_encode(smart_bytes(self.user.id))
        self.token = PasswordResetTokenGenerator().make_token(self.user)

    # 비밀번호 재설정 성공
    def test_password_set_success(self):
        response = self.client.put(
            path=reverse("password_reset_confirm"),
            data={
                "password": "Test1234!!",
                "repassword": "Test1234!!",
                "uidb64": self.uidb64,
                "token": self.token,
            },
        )
        self.assertEqual(response.status_code, 200)

    # 비밀번호 재설정 실패(비밀번호 빈칸)
    def test_password_set_password_blank_fail(self):
        response = self.client.put(
            path=reverse("password_reset_confirm"),
            data={
                "password": "",
                "repassword": "Test1234!!",
                "uidb64": self.uidb64,
                "token": self.token,
            },
        )
        self.assertEqual(response.status_code, 400)

    # 비밀번호 재설정 실패(비밀번호 확인 빈칸)
    def test_password_set_password_confirm_blank_fail(self):
        response = self.client.put(
            path=reverse("password_reset_confirm"),
            data={
                "password": "Test1234!!",
                "repassword": "",
                "uidb64": self.uidb64,
                "token": self.token,
            },
        )
        self.assertEqual(response.status_code, 400)

    # 비밀번호 재설정 실패(비밀번호 유효성검사(simple))
    def test_password_set_password_validation_fail(self):
        response = self.client.put(
            path=reverse("password_reset_confirm"),
            data={
                "password": "Test1234",
                "repassword": "Test1234",
                "uidb64": self.uidb64,
                "token": self.token,
            },
        )
        self.assertEqual(response.status_code, 400)

    # 비밀번호 재설정 실패(비밀번호, 비밀번호 확인 일치 )
    def test_password_set_password_same_fail(self):
        response = self.client.put(
            path=reverse("password_reset_confirm"),
            data={
                "password": "Test1234!!",
                "repassword": "Test1234!",
                "uidb64": self.uidb64,
                "token": self.token,
            },
        )
        self.assertEqual(response.status_code, 400)

    # 토큰이 다를 경우
    def test_password_set_password_token_fail(self):
        response = self.client.put(
            path=reverse("password_reset_confirm"),
            data={
                "password": "Test1234!!",
                "repassword": "Test1234!!",
                "uidb64": self.uidb64,
                "token": "1234",
            },
        )
        self.assertEqual(response.status_code, 401)


class ObtainUserTokenAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.user_data = {"email": "test@test.com", "password":"Test1234!"}
        self.user = User.objects.create_user("test@test.com","test","Test1234!")
    
    def setUp(self):
        self.access_token = self.client.post(reverse("token_obtain_pair"), self.user_data).data["access"]

    # 회원정보 인증 토큰 발급 성공
    def test_obtain_token_success(self):
        response = self.client.post(
            path=reverse("user_token"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"email":"test@test.com", "password":"Test1234!"} 
        )
        self.assertEqual(response.status_code, 200)

    # 회원정보 인증 토큰 발급 실패 (비회원)
    def test_obtain_token_anonymous_fail(self):
        response = self.client.post(
            path=reverse("user_token"),
            data={"email":"test@test.com", "password":"Test1234!"} 
        )
        self.assertEqual(response.status_code, 401)

    # 회원정보 인증 토큰 발급 실패 (이메일 불일치) 
    def test_obtain_token_email_mismatch_fail(self):
        response = self.client.post(
            path=reverse("user_token"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"email":"test1@test.com", "password":"Test1234!"} 
        )
        self.assertEqual(response.status_code, 400)

    # 회원정보 인증 토큰 발급 실패 (이메일 유효성검사) 
    def test_obtain_token_email_validation_fail(self):
        response = self.client.post(
            path=reverse("user_token"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"email":"test1", "password":"Test1234!"} 
        )
        self.assertEqual(response.status_code, 400)

    # 회원정보 인증 토큰 발급 실패 (이메일 blank) 
    def test_obtain_token_email_blank_fail(self):
        response = self.client.post(
            path=reverse("user_token"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"email":"", "password":"Test1234!"} 
        )
        self.assertEqual(response.status_code, 400)

    # 회원정보 인증 토큰 발급 실패 (이메일 required) 
    def test_obtain_token_email_required_fail(self):
        response = self.client.post(
            path=reverse("user_token"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"password":"Test1234!"} 
        )
        self.assertEqual(response.status_code, 400)
    
    # 회원정보 인증 토큰 발급 실패 (비밀번호 불일치) 
    def test_obtain_token_password_mismatch_fail(self):
        response = self.client.post(
            path=reverse("user_token"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"email":"test@test.com", "password":"Test1234"} 
        )
        self.assertEqual(response.status_code, 400)

    # 회원정보 인증 토큰 발급 실패 (비밀번호 blank) 
    def test_obtain_token_password_blank_fail(self):
        response = self.client.post(
            path=reverse("user_token"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"email":"test@test.com", "password":""} 
        )
        self.assertEqual(response.status_code, 400)

    # 회원정보 인증 토큰 발급 실패 (비밀번호 required) 
    def test_obtain_token_password_required_fail(self):
        response = self.client.post(
            path=reverse("user_token"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"email":"test@test.com"}
        )
        self.assertEqual(response.status_code, 400)