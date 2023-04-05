from rest_framework.test import APITestCase

from django.urls import reverse

from users.models import User
from paintings.models import Painting
from auctions.models import Auction

from django.utils import timezone


# class AuctionListAPIViewTest(APITestCase):
#     # 경매 리스트 조회 성공
#     def test_auction_list_success(self):
#         response = self.client.get(
#             path=reverse("auction_list"),
#         )
#         self.assertEqual(response.status_code, 200)

# class AuctionMyListAPIViewTest(APITestCase):
#     @classmethod
#     def setUpTestData(self):
#         self.user_data_1 = {"email": "test@test.com", "password":"Test1234!"}
#         self.user_data_2 = {"email": "test1@test.com", "password":"Test1234!"}
#         self.user1 = User.objects.create_user("test@test.com","test","Test1234!")
#         self.user2 = User.objects.create_user("test1@test.com", "test1", "Test1234!")
#         self.painting = Painting.objects.create(title="title",content="content", owner=self.user1, author=self.user1)
#         self.auction = Auction.objects.create(painting=self.painting, start_bid="10000", now_bid="10000", end_date=timezone.now(), seller=self.user1)

#     def setUp(self):
#         self.user_1_access_token = self.client.post(reverse('token_obtain_pair'), self.user_data_1).data['access']
#         self.user_2_access_token = self.client.post(reverse('token_obtain_pair'), self.user_data_2).data['access']

#     # 나의 경매 리스트 조회 성공
#     def test_auction_my_list_success(self):
#         response = self.client.get(
#             path=reverse("auction_mylist"),
#             HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}"
#         )
#         self.assertEqual(response.status_code, 200)

#     # 나의 경매 리스트 조회 실패(not found)
#     def test_auction_my_list_not_found_fail(self):
#         response = self.client.get(
#             path=reverse("auction_mylist"),
#             HTTP_AUTHORIZATION=f"Bearer {self.user_2_access_token}"
#         )
#         self.assertEqual(response.status_code, 404)

# class AuctionCreateAPIViewTest(APITestCase):
#     @classmethod
#     def setUpTestData(self):
#         self.user_data_1 = {"email": "test@test.com", "password":"Test1234!"}
#         self.user_data_2 = {"email": "test1@test.com", "password":"Test1234!"}
#         self.auction_data = {"start_bid":"10000", "now_bid":"10000", "end_date":timezone.now() + timezone.timedelta(days=1)}
#         self.user1 = User.objects.create_user("test@test.com","test","Test1234!")
#         self.user2 = User.objects.create_user("test1@test.com", "test1", "Test1234!")
#         self.painting_1 = Painting.objects.create(title="title",content="content", owner=self.user1, author=self.user1)
#         self.painting_2 = Painting.objects.create(title="title",content="content", owner=self.user1, author=self.user1)
#         self.auction = Auction.objects.create(painting=self.painting_1, start_bid="10000", now_bid="10000", end_date=timezone.now()+ timezone.timedelta(days=1), seller=self.user1)
        
#     def setUp(self):
#         self.user_1_access_token = self.client.post(reverse('token_obtain_pair'), self.user_data_1).data['access']
#         self.user_2_access_token = self.client.post(reverse('token_obtain_pair'), self.user_data_2).data['access']

#     # 경매 생성 성공
#     def test_auction_create_success(self):
#         response = self.client.post(
#             path=reverse("auction_create", kwargs={"painting_id": self.painting_2.id}),
#             HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
#             data=self.auction_data,
#         )
#         self.assertEqual(response.status_code, 200)

#     # 경매 생성 실패(registered auction)
#     def test_auction_create_fail(self):
#         response = self.client.post(
#             path=reverse("auction_create", kwargs={"painting_id": self.painting_1.id}),
#             HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
#             data=self.auction_data,
#         )
#         self.assertEqual(response.status_code, 400)

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

    #  경매 상세 조회 성공
    def test_auction_view_success(self):
        response = self.client.get(
            path=reverse("auction_detail", kwargs={"auction_id": self.auction_1.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
        )
        self.assertEqual(response.status_code, 200)

    #  경매 상세 조회 실패(not found)
    def test_auction_view_fail(self):
        response = self.client.get(
            path=reverse("auction_detail", kwargs={"auction_id": 1000}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
        )
        self.assertEqual(response.status_code, 404)
    # ------------------------------------------------------------------
    # # 경매 낙찰 성공
    # def test_auction_Successful_bid_success(self):
    #     response = self.client.post(
    #         path=reverse("auction_detail", kwargs={"auction_id": self.auction.id}),
    #         HTTP_AUTHORIZATION=f"Bearer {self.user_1_access_token}",
    #         data={},
    #     )
    #     self.assertEqual(response.status_code, 200)
    # --------------------------------------------------------

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

    # # 경매 입찰 실패(highest bidder)
    # def test_auction_highest_bidder_fail(self):
    #     response = self.client.put(
    #         path=reverse("auction_detail", kwargs={"auction_id": self.auction_2.id}),
    #         HTTP_AUTHORIZATION=f"Bearer {self.user_2_access_token}",
    #         data={"now_bid": "2000"}
    #     )
    #     self.assertEqual(response.status_code, 400)

    # # 경매 입찰 실패(user sufficient points)
    # def test_user_sufficient_points_fail(self):
    #     response = self.client.put(
    #         path=reverse("auction_detail", kwargs={"auction_id": self.auction_1.id}),
    #         HTTP_AUTHORIZATION=f"Bearer {self.user_2_access_token}",
    #         data={"now_bid": "20000"}
    #     )
    #     self.assertEqual(response.status_code, 400)
    
    # # 경매 입찰 실패(bid_increment)
    # def test_auction_bid_increment_fail(self):
    #     response = self.client.put(
    #         path=reverse("auction_detail", kwargs={"auction_id": self.auction_1.id}),
    #         HTTP_AUTHORIZATION=f"Bearer {self.user_2_access_token}",
    #         data={"now_bid": "1110"}
    #     )
    #     self.assertEqual(response.status_code, 400)

    # # 경매 입찰 실패(enter bid against start bid)
    # def test_auction_enter_bid_against_start_bid_fail(self):
    #     response = self.client.put(
    #         path=reverse("auction_detail", kwargs={"auction_id": self.auction_1.id}),
    #         HTTP_AUTHORIZATION=f"Bearer {self.user_2_access_token}",
    #         data={"now_bid": "1000"}
    #     )
    #     self.assertEqual(response.status_code, 400)

    # # 경매 입찰 실패(enter bid against now bid)
    # def test_auction_enter_bid_against_now_bid_fail(self):
    #     response = self.client.put(
    #         path=reverse("auction_detail", kwargs={"auction_id": self.auction_1.id}),
    #         HTTP_AUTHORIZATION=f"Bearer {self.user_2_access_token}",
    #         data={"now_bid": "1000"}
    #     )
    #     self.assertEqual(response.status_code, 400)

    