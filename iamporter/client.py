from requests import Session
from requests.adapters import HTTPAdapter

from .base import *
from .errors import ImpUnAuthorized, ImpApiError
from .api import *

__all__ = ['Iamporter']


class Iamporter:
    """Iamport Client 객체
    api-level의 api Class를 보다 사용하기 편하게 wrapping한 객체

    Attributes:
        imp_auth (IamportAuth): 아임포트 인증 인스턴스
        requests_session (Session): 아임포트 API 호출에 사용될 세션 객체
    """

    def __init__(self, imp_key=None, imp_secret=None, imp_auth=None):
        """
        imp_key와 imp_secret을 전달하거나 IamportAuth 인스턴스를 직접 imp_auth로 넘겨 초기화할 수 있습니다.

        Args:
            imp_key (str): Iamport REST API Key
            imp_secret (str): Iamport REST API Secret
            imp_auth (IamportAuth): IamportAuth 인증 인스턴스
        """
        if isinstance(imp_auth, IamportAuth):
            self.imp_auth = imp_auth
        elif imp_key and imp_secret:
            self.imp_auth = IamportAuth(imp_key, imp_secret)
        else:
            raise ImpUnAuthorized("인증정보가 전달되지 않았습니다.")

        self.requests_session = Session()
        requests_adapter = HTTPAdapter(max_retries=3)
        self.requests_session.mount('https://', requests_adapter)

    def find(self, imp_uid=None, merchant_uid=None):
        """아임포트 고유번호 또는 가맹점지정 고유번호로 결제내역을 확인합니다

        Args:
            imp_uid (str): 아임포트 고유번호
            merchant_uid (str): 결제요청 시 가맹점에서 요청한 merchant_uid

        Returns:
            dict
        """
        api_instance = Payments(auth=self.imp_auth, session=self.requests_session)
        if imp_uid:
            response = api_instance.get(imp_uid)
        elif merchant_uid:
            response = api_instance.get_find(merchant_uid)
        else:
            raise KeyError('imp_uid와 merchant_uid 중 하나를 반드시 지정해야합니다.')

        if not response.is_succeed:
            raise ImpApiError(response)

        return response.data