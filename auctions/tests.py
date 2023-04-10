from rest_framework.test import APITestCase

from django.urls import reverse

from users.models import User
from paintings.models import Painting
from auctions.models import Auction, AuctionHistory, Comment

from django.utils import timezone


# 경매 리스트 조회
class AuctionListAPIViewTest(APITestCase):
    # 경매 리스트 조회 성공
    def test_auction_list_success(self):
        response = self.client.get(
            path=reverse("auction_list"),
        )
        self.assertEqual(response.status_code, 200)

# 나의 경매 리스트 조회
class AuctionMyListAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.user_data_1 = {"email": "test@test.com", "password":"Test1234!"}
        self.user_data_2 = {"email": "test1@test.com", "password":"Test1234!"}
        self.user1 = User.objects.create_user("test@test.com","test","Test1234!")
        self.user2 = User.objects.create_user("test1@test.com", "test1", "Test1234!")
        self.painting = Painting.objects.create(title="title",content="content", owner=self.user1, author=self.user1)
        self.auction = Auction.objects.create(painting=self.painting, start_bid="10000", now_bid="10000", end_date=timezone.now(), seller=self.user1)

    def setUp(self):
        self.user_1_access_token = self.client.post(reverse('token_obtain_pair'), self.user_data_1).data['access']
        self.user_2_access_token = self.client.post(reverse('token_obtain_pair'), self.user_data_2).data['access']

    # 나의 경매 리스트 조회 성공
    def test_auction_my_list_success(self):
        response = self.client.get(
            path=reverse("auction_mylist"),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}"
        )
        self.assertEqual(response.status_code, 200)

    # 나의 경매 리스트 조회 실패(not found)
    def test_auction_my_list_not_found_fail(self):
        response = self.client.get(
            path=reverse("auction_mylist"),
            HTTP_AUTHORIZATION=f"Bearer {self.user_2_access_token}"
        )
        self.assertEqual(response.status_code, 404)

# 경매 생성
class AuctionCreateAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.user_data_1 = {"email": "test@test.com", "password":"Test1234!"}
        self.user_data_2 = {"email": "test1@test.com", "password":"Test1234!"}
        self.auction_data = {"start_bid":"10000", "now_bid":"10000", "end_date":timezone.now() + timezone.timedelta(days=1)}
        self.user1 = User.objects.create_user("test@test.com","test","Test1234!")
        self.user2 = User.objects.create_user("test1@test.com", "test1", "Test1234!")
        self.painting_1 = Painting.objects.create(title="title",content="content", owner=self.user1, author=self.user1)
        self.painting_2 = Painting.objects.create(title="title",content="content", owner=self.user1, author=self.user1)
        self.auction = Auction.objects.create(painting=self.painting_1, start_bid="10000", now_bid="10000", end_date=timezone.now()+ timezone.timedelta(days=1), seller=self.user1)
        
    def setUp(self):
        self.user_1_access_token = self.client.post(reverse('token_obtain_pair'), self.user_data_1).data['access']
        self.user_2_access_token = self.client.post(reverse('token_obtain_pair'), self.user_data_2).data['access']

    # 경매 생성 성공
    def test_auction_create_success(self):
        response = self.client.post(
            path=reverse("auction_create", kwargs={"painting_id": self.painting_2.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
            data=self.auction_data,
        )
        self.assertEqual(response.status_code, 200)

    # 경매 생성 실패(registered auction)
    def test_auction_create_fail(self):
        response = self.client.post(
            path=reverse("auction_create", kwargs={"painting_id": self.painting_1.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
            data=self.auction_data,
        )
        self.assertEqual(response.status_code, 400)

class AuctionDetailAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.user_data_1 = {"email": "test@test.com", "password":"Test1234!", "point":"100000"}
        self.user_data_2 = {"email": "test1@test.com", "password":"Test1234!", "point":"100000"}
        self.user1 = User.objects.create_user(email="test@test.com",nickname="test",password="Test1234!")
        self.user2 = User.objects.create_user(email="test1@test.com", nickname="test1", password="Test1234!")
        self.painting_1 = Painting.objects.create(title="title",content="content", owner=self.user1, author=self.user1)
        self.auction_1 = Auction.objects.create(start_bid="1000", now_bid="1100", end_date=timezone.now() + timezone.timedelta(days=1), painting=self.painting_1, seller=self.user1, bidder=self.user1)
        self.auction_2 = Auction.objects.create(start_bid="1000", now_bid="1100", end_date=timezone.now() + timezone.timedelta(days=1), painting=self.painting_1, seller=self.user1, bidder=self.user2)
        self.auction_3 = Auction.objects.create(start_bid="1000", now_bid="1100", end_date=timezone.now() - timezone.timedelta(days=1), painting=self.painting_1, seller=self.user1, bidder=self.user1)
        
    def setUp(self):
        self.user_1_access_token = self.client.post(reverse('token_obtain_pair'), self.user_data_1).data['access']
        self.user_2_access_token = self.client.post(reverse('token_obtain_pair'), self.user_data_2).data['access']

    # 경매 상세 조회
    # 경매 상세 조회 성공
    def test_auction_detail_success(self):
        response = self.client.get(
            path=reverse("auction_detail", kwargs={"auction_id": self.auction_1.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
        )
        self.assertEqual(response.status_code, 200)

    #  경매 상세 조회 실패(not found)
    def test_auction_detail_fail(self):
        response = self.client.get(
            path=reverse("auction_detail", kwargs={"auction_id": 10}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
        )
        self.assertEqual(response.status_code, 404)

    # 경매 입찰
    # 경매 입찰 성공
    def test_auction_bid_success(self):
        response = self.client.put(
            path=reverse("auction_detail", kwargs={"auction_id": self.auction_1.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_2_access_token}",
            data={"now_bid": "2000"}
        )
        self.assertEqual(response.status_code, 200)
    
    # 경매 입찰 실패(anonymous)
    def test_auction_bid_anonymous_fail(self):
        response = self.client.put(
            path=reverse("auction_detail", kwargs={"auction_id": self.auction_1.id}),
            data={"now_bid": "2000"}
        )
        self.assertEqual(response.status_code, 401)

    # 경매 입찰 실패(not found)
    def test_auction_bid_fail(self):
        response = self.client.put(
            path=reverse("auction_detail", kwargs={"auction_id": 10}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_2_access_token}",
            data={"now_bid": "2000"}
        )
        self.assertEqual(response.status_code, 404)

    # 경매 입찰 실패(closed auction)
    def test_closed_auction_fail(self):
        response = self.client.put(
            path=reverse("auction_detail", kwargs={"auction_id": self.auction_3.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_2_access_token}",
            data={"now_bid": "2000"}
        )
        self.assertEqual(response.status_code, 400)

    # 경매 입찰 실패(highest bidder)
    def test_auction_highest_bidder_fail(self):
        response = self.client.put(
            path=reverse("auction_detail", kwargs={"auction_id": self.auction_2.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_2_access_token}",
            data={"now_bid": "2000"}
        )
        self.assertEqual(response.status_code, 400)

    # 경매 입찰 실패(user sufficient points)
    def test_user_sufficient_points_fail(self):
        response = self.client.put(
            path=reverse("auction_detail", kwargs={"auction_id": self.auction_1.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_2_access_token}",
            data={"now_bid": "20000"}
        )
        self.assertEqual(response.status_code, 400)
    
    # 경매 입찰 실패(bid_increment)
    def test_auction_bid_increment_fail(self):
        response = self.client.put(
            path=reverse("auction_detail", kwargs={"auction_id": self.auction_1.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_2_access_token}",
            data={"now_bid": "1110"}
        )
        self.assertEqual(response.status_code, 400)

    # 경매 입찰 실패(enter bid against start bid)
    def test_auction_enter_bid_against_start_bid_fail(self):
        response = self.client.put(
            path=reverse("auction_detail", kwargs={"auction_id": self.auction_1.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_2_access_token}",
            data={"now_bid": "1000"}
        )
        self.assertEqual(response.status_code, 400)

    # 경매 입찰 실패(enter bid against now bid)
    def test_auction_enter_bid_against_now_bid_fail(self):
        response = self.client.put(
            path=reverse("auction_detail", kwargs={"auction_id": self.auction_1.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_2_access_token}",
            data={"now_bid": "1000"}
        )
        self.assertEqual(response.status_code, 400)

    # 경매 삭제
    #  경매 삭제 성공
    def test_auction_delete_success(self):
        response = self.client.delete(
            path=reverse("auction_detail", kwargs={"auction_id": self.auction_1.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
        )
        self.assertEqual(response.status_code, 200)

    #  경매 삭제 실패(not found)
    def test_auction_delete_fail(self):
        response = self.client.delete(
            path=reverse("auction_detail", kwargs={"auction_id": 10}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
        )
        self.assertEqual(response.status_code, 404)

    #  경매 삭제 실패(anonymous)
    def test_auction_delete_anonymous_fail(self):
        response = self.client.delete(
            path=reverse("auction_detail", kwargs={"auction_id": self.auction_1.id}),
        )
        self.assertEqual(response.status_code, 401)

    #  경매 삭제 실패(access denied)
    def test_auction_delete_access_denied(self):
        response = self.client.delete(
            path=reverse("auction_detail", kwargs={"auction_id": self.auction_1.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_2_access_token}",
        )
        self.assertEqual(response.status_code, 403)

    
# 경매 좋아요
class AuctionLikeAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.user_data_1 = {"email": "test@test.com", "password":"Test1234!", "point":"100000"}
        self.user1 = User.objects.create_user(email="test@test.com",nickname="test",password="Test1234!")
        self.painting_1 = Painting.objects.create(title="title",content="content", owner=self.user1, author=self.user1)
        self.auction_1 = Auction.objects.create(start_bid="1000", now_bid="1100", end_date=timezone.now() + timezone.timedelta(days=1), painting=self.painting_1, seller=self.user1, bidder=self.user1)
        
    def setUp(self):
        self.user_1_access_token = self.client.post(reverse('token_obtain_pair'), self.user_data_1).data['access']
     
    # 경매 좋아요 성공
    def test_auction_like_success(self):
        response = self.client.post(
            path=reverse("auction_like", kwargs={"auction_id": self.auction_1.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
        )
        self.assertEqual(response.status_code, 200)

    # 경매 좋아요 실패(not found)
    def test_auction_like_fail(self):
        response = self.client.post(
            path=reverse("auction_like", kwargs={"auction_id": 10}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
        )
        self.assertEqual(response.status_code, 404)

    # 경매 좋아요 실패(anonymous)
    def test_auction_like_anonymous_fail(self):
        response = self.client.post(
            path=reverse("auction_like", kwargs={"auction_id": self.auction_1.id}),
        )
        self.assertEqual(response.status_code, 401)


# 경매 거래내역
class AuctionHistoryAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.user_data_1 = {"email": "test@test.com", "password":"Test1234!", "point":"100000"}
        self.user1 = User.objects.create_user(email="test@test.com",nickname="test",password="Test1234!")
        self.painting_1 = Painting.objects.create(title="title",content="content", owner=self.user1, author=self.user1)
        self.auction_1 = Auction.objects.create(start_bid="1000", now_bid="1100", end_date=timezone.now() + timezone.timedelta(days=1), painting=self.painting_1, seller=self.user1, bidder=self.user1)
        self.auction_history = AuctionHistory.objects.create(auction=self.auction_1, bidder=self.user1, now_bid="1100")
    
    def setUp(self):
        self.user_1_access_token = self.client.post(reverse('token_obtain_pair'), self.user_data_1).data['access']

    # 경매 거래내역 조회 성공
    def test_auction_history_view_success(self):
        response = self.client.get(
            path=reverse("auction_history", kwargs={"auction_id": self.auction_1.id}),
        )
        self.assertEqual(response.status_code, 200)

class CommentAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.user_data_1 = {"email": "test@test.com", "password":"Test1234!", "point":"100000"}
        self.user_data_2 = {"email": "test1@test.com", "password":"Test1234!", "point":"100000"}
        self.user1 = User.objects.create_user(email="test@test.com",nickname="test",password="Test1234!")
        self.user2 = User.objects.create_user(email="test1@test.com", nickname="test1", password="Test1234!")
        self.painting_1 = Painting.objects.create(title="title",content="content", owner=self.user1, author=self.user1)
        self.auction_1 = Auction.objects.create(start_bid="1000", now_bid="1100", end_date=timezone.now() + timezone.timedelta(days=1), painting=self.painting_1, seller=self.user1, bidder=self.user1)
        
    def setUp(self):
        self.user_1_access_token = self.client.post(reverse('token_obtain_pair'), self.user_data_1).data['access']
        self.user_2_access_token = self.client.post(reverse('token_obtain_pair'), self.user_data_2).data['access']

    # 댓글 조회
    # 해당 경매 댓글 전체 조회 성공
    def test_comment_list_success(self):
        response = self.client.get(
            path=reverse("comment", kwargs={"auction_id": self.auction_1.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
        )
        self.assertEqual(response.status_code, 200)

    # 해당 경매 댓글 전체 조회 실패(not found)
    def test_comment_list_fail(self):
        response = self.client.get(
            path=reverse("comment", kwargs={"auction_id": 10}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
        )
        self.assertEqual(response.status_code, 404)

    # 해당 경매 댓글 전체 조회 실패(anonymous)
    def test_comment_list_anonymous_fail(self):
        response = self.client.get(
            path=reverse("comment", kwargs={"auction_id": self.auction_1.id}),
        )
        self.assertEqual(response.status_code, 401)

    # 댓글 생성
    # 댓글 생성 성공
    def test_comment_create_success(self):
        response = self.client.post(
            path=reverse("comment", kwargs={"auction_id": self.auction_1.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
            data={"content":"test content"}
        )
        self.assertEqual(response.status_code, 201)

    # 댓글 생성 실패(anonymous)
    def test_comment_create_anonymous_fail(self):
        response = self.client.post(
            path=reverse("comment", kwargs={"auction_id": self.auction_1.id}),
            data={"content":"test content"}
        )
        self.assertEqual(response.status_code, 401)

    # 댓글 생성 실패(no content)
    def test_comment_create_fail(self):
        response = self.client.post(
            path=reverse("comment", kwargs={"auction_id": self.auction_1.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
            data={"content":""}
        )
        self.assertEqual(response.status_code, 400)

class CommentDetailAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.user_data_1 = {"email": "test@test.com", "password":"Test1234!", "point":"100000"}
        self.user_data_2 = {"email": "test1@test.com", "password":"Test1234!", "point":"100000"}
        self.user1 = User.objects.create_user(email="test@test.com",nickname="test",password="Test1234!")
        self.user2 = User.objects.create_user(email="test1@test.com", nickname="test1", password="Test1234!")
        self.painting_1 = Painting.objects.create(title="title",content="content", owner=self.user1, author=self.user1)
        self.auction_1 = Auction.objects.create(start_bid="1000", now_bid="1100", end_date=timezone.now() + timezone.timedelta(days=1), painting=self.painting_1, seller=self.user1, bidder=self.user1)
        self.comment_1=Comment.objects.create(content="test content", auction=self.auction_1, user=self.user1)
        
    def setUp(self):
        self.user_1_access_token = self.client.post(reverse('token_obtain_pair'), self.user_data_1).data['access']
        self.user_2_access_token = self.client.post(reverse('token_obtain_pair'), self.user_data_2).data['access']

    # 댓글 상세 조회
    # 댓글 상세 조회 성공
    def test_comment_detail_success(self):
        response = self.client.get(
            path=reverse("comment_detail", kwargs={"auction_id": self.auction_1.id, "comment_id":self.comment_1.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
        )
        self.assertEqual(response.status_code, 200)

    # 댓글 상세 조회 실패(not found)
    def test_comment_detail_fail(self):
        response = self.client.get(
            path=reverse("comment_detail", kwargs={"auction_id": self.auction_1.id, "comment_id":10}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
        )
        self.assertEqual(response.status_code, 404)

    # 댓글 상세 조회 실패(anonymous)
    def test_comment_detail_anonymous_fail(self):
        response = self.client.get(
            path=reverse("comment_detail", kwargs={"auction_id": self.auction_1.id, "comment_id":self.comment_1.id}),
        )
        self.assertEqual(response.status_code, 401)

    # 댓글 수정
    # 댓글 수정 성공
    def test_comment_edit_success(self):
        response = self.client.put(
            path=reverse("comment_detail", kwargs={"auction_id": self.auction_1.id, "comment_id":self.comment_1.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
            data={"content":"edit content"}
        )
        self.assertEqual(response.status_code, 200)

    # 댓글 수정 실패(no content)
    def test_comment_edit_fail(self):
        response = self.client.put(
            path=reverse("comment_detail", kwargs={"auction_id": self.auction_1.id, "comment_id":self.comment_1.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
            data={"content":""}
        )
        self.assertEqual(response.status_code, 400)

    # 댓글 수정 실패(not found)
    def test_comment_edit_not_found_fail(self):
        response = self.client.put(
            path=reverse("comment_detail", kwargs={"auction_id": self.auction_1.id, "comment_id":10}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
            data={"content":"edit content"}
        )
        self.assertEqual(response.status_code, 404)

    # 댓글 수정 실패(anonymous)
    def test_comment_edit_anonymous_fail(self):
        response = self.client.put(
            path=reverse("comment_detail", kwargs={"auction_id": self.auction_1.id, "comment_id":self.comment_1.id}),
            data={"content":"edit content"}
        )
        self.assertEqual(response.status_code, 401)

    # 댓글 수정 실패(access denied)
    def test_comment_edit_access_denied_fail(self):
        response = self.client.put(
            path=reverse("comment_detail", kwargs={"auction_id": self.auction_1.id, "comment_id":self.comment_1.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_2_access_token}",
            data={"content":"edit content"}
        )
        self.assertEqual(response.status_code, 403)

    # 댓글 삭제
    # 댓글 삭제 성공
    def test_comment_delete_success(self):
        response = self.client.delete(
            path=reverse("comment_detail", kwargs={"auction_id": self.auction_1.id, "comment_id":self.comment_1.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
        )
        self.assertEqual(response.status_code, 200)

    # 댓글 삭제 실패(not found)
    def test_comment_delete_not_found_fail(self):
        response = self.client.delete(
            path=reverse("comment_detail", kwargs={"auction_id": self.auction_1.id, "comment_id":10}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
        )
        self.assertEqual(response.status_code, 404)

    # 댓글 삭제 실패(anonymous)
    def test_comment_delete_anonymous_fail(self):
        response = self.client.delete(
            path=reverse("comment_detail", kwargs={"auction_id": self.auction_1.id, "comment_id":self.comment_1.id}),
        )
        self.assertEqual(response.status_code, 401)

    # 댓글 삭제 실패(access denied)
    def test_comment_delete_access_denied_fail(self):
        response = self.client.delete(
            path=reverse("comment_detail", kwargs={"auction_id": self.auction_1.id, "comment_id":self.comment_1.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_2_access_token}",
        )
        self.assertEqual(response.status_code, 403)



    