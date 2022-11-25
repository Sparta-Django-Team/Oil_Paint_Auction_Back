from django.urls import reverse

from rest_framework.test import APITestCase

from .models import User

class UserSignupAPIViewTestCase(APITestCase):
    
    #회원가입 성공
    def test_signup_success(self):
        url = reverse("user_view")
        user_data = {
            "email":"test@test.com",
            "nickname":"test",
            "password":"Test1234!",
            "repassword":"Test1234!",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 201)
    
    #회원가입 실패(이메일 빈칸)
    def test_signup_email_blank_fail(self):
        url = reverse("user_view")
        user_data = {
            "email":"",
            "nickname":"test",
            "password":"Test1234!",
            "repassword":"Test1234!",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
        
    #회원가입 실패(이메일 형식)
    def test_signup_email_invalid_fail(self):
        url = reverse("user_view")
        user_data = {
            "email":"test",
            "nickname":"test",
            "password":"Test1234!",
            "repassword":"Test1234!",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
        
    #회원가입 실패(이메일 중복)
    def test_signup_email_unique_fail(self):
        User.objects.create_user("test@test.com","test","Test1234!")
        url = reverse("user_view")
        user_data = {
            "email":"test@test.com",
            "nickname":"test1",
            "password":"Test1234!",
            "repassword":"Test1234!",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
        
    #회원가입 실패(닉네임 빈칸)
    def test_signup_nickname_blank_fail(self):
        url = reverse("user_view")
        user_data = {
            "email":"test@test.com",
            "nickname":"",
            "password":"Test1234!",
            "repassword":"Test1234!",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
        
    #회원가입 실패(닉네임 유효성검사)
    def test_signup_nickname_validation_fail(self):
        url = reverse("user_view")
        user_data = {
            "email":"test@test.com",
            "nickname":"n!",
            "password":"Test1234!",
            "repassword":"Test1234!",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
    
    #회원가입 실패(닉네임 중복)
    def test_signup_nickname_unique_fail(self):
        User.objects.create_user("test@test.com","test","Test1234!")
        url = reverse("user_view")
        user_data = {
            "email":"test1@test.com",
            "nickname":"test",
            "password":"Test1234!",
            "repassword":"Test1234!",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
    
    #회원가입 실패(비밀번호 빈칸)
    def test_signup_password_blank_fail(self):
        url = reverse("user_view")
        user_data = {
            "email":"test@test.com",
            "nickname":"test",
            "password":"",
            "repassword":"Test1234!",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
        
    #회원가입 실패(비밀번호확인 빈칸)
    def test_signup_password_confirm_blank_fail(self):
        url = reverse("user_view")
        user_data = {
            "email":"test@test.com",
            "nickname":"test",
            "password":"Test1234!",
            "repassword":"",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
        
    #회원가입 실패(비밀번호, 비밀번호 확인 일치 )
    def test_signup_password_same_fail(self):
        url = reverse("user_view")
        user_data = {
            "email":"test@test.com",
            "nickname":"test",
            "password":"Test1234!",
            "repassword":"Test12345!",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
        
    #회원가입 실패(비밀번호 유효성 검사(simple))
    def test_signup_password_validation_fail(self):
        url = reverse("user_view")
        user_data = {
            "email":"test@test.com",
            "nickname":"test",
            "password":"t1",
            "repassword":"t1",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
        
    #회원가입 실패(비밀번호 유효성검사(동일))
    def test_signup_password_validation_same_fail(self):
        url = reverse("user_view")
        user_data = {
            "email":"test@test.com",
            "nickname":"test",
            "password":"Test111!",
            "repassword":"Test111!",
            "term_check":"True",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
        
    #회원가입 실패(약관동의)
    def test_signup_term_checkt_fail(self):
        url = reverse("user_view")
        user_data = {
            "email":"test@test.com",
            "nickname":"test",
            "password":"Test111!",
            "repassword":"Test111!",
            "term_check":"False",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)

class UserAPIViewTestCase(APITestCase):
    def setUp(self):
        self.data = {"email": "test@test.com", "password":"Test1234!"}
        self.user1 = User.objects.create_user("test@test.com","test","Test1234!")
        self.user2 = User.objects.create_user("test1@test.com", "test1", "Test1234!")
    
    #회원정보 수정 성공
    def test_user_update_success(self):
        access_token = self.client.post(reverse('token_obtain_pair'), self.data).data['access']
        response = self.client.put(
            path=reverse("user_view"),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
            data={"nickname":"test11"} 
        )
        self.assertEqual(response.status_code, 200)
        
    #회원정보 수정 실패(닉네임 유효성검사)
    def test_user_update_nickname_validation_fail(self):
        access_token = self.client.post(reverse('token_obtain_pair'), self.data).data['access']
        response = self.client.put(
            path=reverse("user_view"),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
            data={"nickname":"t!"} 
        )
        self.assertEqual(response.status_code, 400)
    
    #회원정보 수정 실패(닉네임 중복)
    def test_user_update_nickname_unique_fail(self):
        access_token = self.client.post(reverse('token_obtain_pair'), self.data).data['access']
        response = self.client.put(
            path=reverse("user_view"),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
            data={"nickname":"test1"} 
        )
        self.assertEqual(response.status_code, 400)
    
    #회원정보 수정 실패(닉네임 빈칸)
    def test_user_update_nickname_blank_fail(self):
        access_token = self.client.post(reverse('token_obtain_pair'), self.data).data['access']
        response = self.client.put(
            path=reverse("user_view"),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
            data={"nickname":"","password":"Test1234!", "repassword":"Test1234!"} #비밀번호가 필수값으로 들어가버린다.
        )
        self.assertEqual(response.status_code, 400)
    
    #회원 비활성화 성공
    def test_user_delete_success(self):
        access_token = self.client.post(reverse('token_obtain_pair'), self.data).data['access']
        response = self.client.delete(
            path=reverse("user_view"),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        
class ChangePasswordAPIViewTestCase(APITestCase):
    def setUp(self):
        self.data = {"email": "test@test.com", "password":"Test1234!"}
        self.user = User.objects.create_user("test@test.com","test","Test1234!")
        
    #비밀번호 변경 인증 성공
    def test_password_change_confirm_success(self):
        access_token = self.client.post(reverse('token_obtain_pair'), self.data).data['access']
        response = self.client.post(
            path=reverse("change_password_view"),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
            data={"password":"Test1234!"} 
        )
        self.assertEqual(response.status_code, 200)
    
    #비밀번호 변경 인증 실패
    def test_password_change_confirm_fail(self):
        access_token = self.client.post(reverse('token_obtain_pair'), self.data).data['access']
        response = self.client.post(
            path=reverse("change_password_view"),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
            data={"password":"Test!"} 
        )
        self.assertEqual(response.status_code, 400)
    
    #비밀번호 변경 성공
    def test_password_change_success(self):
        access_token = self.client.post(reverse('token_obtain_pair'), self.data).data['access']
        response = self.client.put(
            path=reverse("change_password_view"),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
            data={"password":"Test1234!!", "repassword":"Test1234!!"} 
        )
        self.assertEqual(response.status_code, 200)
    
    #비밀번호 변경 실패(비밀번호 빈칸)
    def test_password_change_password_blank_fail(self):
        access_token = self.client.post(reverse('token_obtain_pair'), self.data).data['access']
        response = self.client.put(
            path=reverse("change_password_view"),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
            data={"password":"", "repassword":"Test1234!!"} 
        )
        self.assertEqual(response.status_code, 400)

    #비밀번호 변경 실패(비밀번호 확인 빈칸)
    def test_password_change_password_confirm_blank_fail(self):
        access_token = self.client.post(reverse('token_obtain_pair'), self.data).data['access']
        response = self.client.put(
            path=reverse("change_password_view"),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
            data={"password":"Test1234!!", "repassword":""} 
        )
        self.assertEqual(response.status_code, 400)
        
    #비밀번호 변경 실패(비밀번호 현재비밀번호와 동일시)
    def test_password_change_current_password_same_fail(self):
        access_token = self.client.post(reverse('token_obtain_pair'), self.data).data['access']
        response = self.client.put(
            path=reverse("change_password_view"),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
            data={"password":"Test1234!", "repassword":"Test1234!"} 
        )
        
        self.assertEqual(response.status_code, 400)
        
    #비밀번호 변경 실패(비밀번호 유효성검사(simple))
    def test_password_change_password_validation_fail(self):
        access_token = self.client.post(reverse('token_obtain_pair'), self.data).data['access']
        response = self.client.put(
            path=reverse("change_password_view"),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
            data={"password":"Test1234", "repassword":"Test1234"} 
        )
        self.assertEqual(response.status_code, 400)
        
    #비밀번호 변경 실패(비밀번호 유효성검사(동일))
    def test_password_change_password_validation_same_fail(self):
        access_token = self.client.post(reverse('token_obtain_pair'), self.data).data['access']
        response = self.client.put(
            path=reverse("change_password_view"),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
            data={"password":"Test111!", "repassword":"Test111!"} 
        )
        self.assertEqual(response.status_code, 400)
    
    #회원가입 실패(비밀번호, 비밀번호 확인 일치 )
    def test_password_change_password_same_fail(self):
        access_token = self.client.post(reverse('token_obtain_pair'), self.data).data['access']
        response = self.client.put(
            path=reverse("change_password_view"),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
            data={"password":"Test1234!!", "repassword":"Test1234!"} 
        )
        self.assertEqual(response.status_code, 400)
        
class LoginUserTest(APITestCase):
    def setUp(self):
        self.success_data = {"email": "test@test.com", "password":"Test1234!"}
        self.fail_data = {"email": "test1@test.com", "password":"Test1234!!"}
        self.user = User.objects.create_user("test@test.com","test","Test1234!")
        
    #로그인 성공
    def test_login_success(self):
        response = self.client.post(reverse('token_obtain_pair'), self.success_data)
        self.assertEqual(response.status_code, 200)
    
    #로그인 실패
    def test_login_fail(self):
        response = self.client.post(reverse('token_obtain_pair'), self.fail_data)
        self.assertEqual(response.status_code, 401)
