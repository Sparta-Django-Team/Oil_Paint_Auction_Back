import sys
import os
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_back.settings')
django.setup()

from django.utils import timezone

from users.models import User
from .utils import Util


#회원정보 보유기간이 지나면 회원상태를 비활성화로 만들어주고 메일을 보낸다.
#리눅스 crontab으로 하루에 한번 씩 자동으로 실행되게 함(서버 배포 이후)
user = User.objects.filter(is_admin=False, retention_period= str(timezone.now().date()))

user_email = user.values("email")

email_subject='오코완 휴면회원 계정 처리 안내'
email_body='고객님 안녕하세요. 오코완입니다. 저희는 소중한 고객님의 개인정보 보호를 위해 관계 법렵에 따라 고객님의 온라인 계정을 별도로 분리 보관할 예정입니다. 휴면계정을 해제하기 위해서는 별도의 인증 동의 절차가 진행될 수 있으므로 편리한 계정 사용이 필요하시다면 지금 바로 오코완을 방문해주세요.'

if user:
    for i in user_email:
        message = {'email_body': email_body, 'to_email': [i["email"]],'email_subject': email_subject}
        Util.send_email(message)
        
    user.update(status="W")

#로그인 시 출석체크 포인트 초기화
User.objects.filter(today_point=True).update(today_point=False)