import requests
from requests.auth import AuthBase

__all__ = ['IamportResponse',
           'IamportError', 'IamportUnAuthorized',
           'IamportAuth',
           'BaseApi', ]

IAMPORT_API_URL = "https://api.iamport.kr/"


class IamportResponse:
    """아임포트 API 응답 객체

    Attributes:
        status (int): API 응답 HTTP 상태 코드
        code (int): API 응답코드
        message (str): API 응답메세지
        data (dict): API 응답 response 데이터
    """

    def __init__(self, requests_response):
        """
        Args:
            requests_response (requests.Response)
        """
        self.status = requests_response.status_code

        body = requests_response.json()
        self.code = body.get('code')
        self.message = body.get('message')
        self.data = body.get('response', {})

    @property
    def is_succeed(self):
        """API 결과가 성공적인지 확인"""
        return self.status == 200 and self.code == 0

    @property
    def raw(self):
        """원본 API 응답"""
        return {
            'code': self.code,
            'message': self.message,
            'response': self.data,
        }


class IamportError(Exception):
    """아임포트 API 오류

    Attributes:
        response (IamportResponse): API 응답 객체
    """

    def __init__(self, response):
        self.response = response


class IamportUnAuthorized(IamportError):
    """아임포트 인증실패 오류"""

    def __init__(self, response):
        super().__init__(response)


class IamportAuth(AuthBase):
    """아임포트 인증 객체

    Attributes:
        token (str): 발급받은 액세스 토큰
    """

    def __init__(self, imp_key, imp_secret, session=None, imp_url=IAMPORT_API_URL):
        """
        Args:
            imp_key (str): 아임포트 API 키
            imp_secret (str): 아임포트 API 시크릿
            session (requests.Session): API 요청에 사용할 requests Session 인스턴스
            imp_url (str): 아임포트 API URL
        """

        self.token = None

        api_endpoint = imp_url + '/users/getToken'
        api_payload = {'imp_key': imp_key, 'imp_secret': imp_secret}

        auth_response = IamportResponse(
            session.post(api_endpoint, data=api_payload) if isinstance(session, requests.Session)
            else requests.post(api_endpoint, data=api_payload)
        )
        if auth_response.is_succeed:
            self.token = auth_response.data.get('access_token', None)

        if self.token is None:
            raise IamportUnAuthorized(auth_response)

    def __call__(self, r):
        r.headers['Authorization'] = self.token
        return r


class BaseApi:
    """모든 API 객체의 공통 요소 상속용 추상 객체

    Attributes:
        requests_session (requests.Session): API 호출에 사용될 requests Session 인스턴스
    """

    def __init__(self, auth, session=None, imp_url=IAMPORT_API_URL):
        """
        Args:
            auth (IamportAuth): 아임포트 API 인증 인스턴스
            session (requests.Session): API 요청에 사용할 requests Session 인스턴스
            imp_url (str): 아임포트 API URL
        """

        self.iamport_auth = auth
        self.requests_session = session
        self.imp_url = imp_url

    def _get(self, endpoint, **kwargs):
        if isinstance(self.requests_session, requests.Session):
            return self.requests_session.get(self.imp_url + endpoint, params=kwargs)
        else:
            return requests.get(self.imp_url + endpoint, params=kwargs)

    def _post(self, endpoint, **kwargs):
        if isinstance(self.requests_session, requests.Session):
            return self.requests_session.post(self.imp_url + endpoint, data=kwargs)
        else:
            return requests.post(self.imp_url + endpoint, data=kwargs)
