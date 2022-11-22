import sys
import os
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_back.settings')
django.setup()

from django.utils import timezone
from users.models import User

#회원정보 보유기간이 지나면 회원상태를 비활성화로 만들어줌
#리눅스 crontab으로 하루에 한번 씩 자동으로 실행되게 함(서버 배포 이후)
user = User.objects.filter(is_admin=False) and User.objects.filter(retention_period= str(timezone.now().date()))
user.update(status="S")