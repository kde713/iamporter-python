from requests import Session
from requests.adapters import HTTPAdapter

from .base import IamportAuth, IamportResponse
from .errors import ImpUnAuthorized, ImpApiError
from .api import Payments, Subscribe
from .consts import IAMPORT_API_URL

__all__ = ['Iamporter']


class Iamporter:
    """Iamport Client 객체
    api-level의 api Class를 보다 사용하기 편하게 wrapping한 객체

    Attributes:
        imp_auth (IamportAuth): 아임포트 인증 인스턴스
        imp_url (str): Iamport REST API Host
        requests_session (Session): 아임포트 API 호출에 사용될 세션 객체
    """

    def __init__(self, imp_key=None, imp_secret=None, imp_auth=None, imp_url=IAMPORT_API_URL):
        """
        imp_key와 imp_secret을 전달하거나 IamportAuth 인스턴스를 직접 imp_auth로 넘겨 초기화할 수 있습니다.

        Args:
            imp_key (str): Iamport REST API Key
            imp_secret (str): Iamport REST API Secret
            imp_auth (IamportAuth): IamportAuth 인증 인스턴스
            imp_url (str): Iamport REST API Host. 기본값은 https://api.iamport.kr/
        """
        if isinstance(imp_auth, IamportAuth):
            self.imp_auth = imp_auth
        elif imp_key and imp_secret:
            self.imp_auth = IamportAuth(imp_key, imp_secret)
        else:
            raise ImpUnAuthorized("인증정보가 전달되지 않았습니다.")

        self.imp_url = imp_url

        self.requests_session = Session()
        requests_adapter = HTTPAdapter(max_retries=3)
        self.requests_session.mount('https://', requests_adapter)

    def __del__(self):
        if getattr(self, 'requests_session', None):
            self.requests_session.close()

    @property
    def _api_kwargs(self):
        return {'auth': self.imp_auth, 'session': self.requests_session, 'imp_url': self.imp_url}

    def _process_response(self, response):
        """
        Args:
            response (IamportResponse)

        Returns:
            dict
        """
        if response.status == 401:
            raise ImpUnAuthorized(response.message)
        if not response.is_succeed:
            raise ImpApiError(response)
        return response.data

    def find_payment(self, imp_uid=None, merchant_uid=None):
        """아임포트 고유번호 또는 가맹점지정 고유번호로 결제내역을 확인합니다

        Args:
            imp_uid (str): 아임포트 고유번호
            merchant_uid (str): 결제요청 시 가맹점에서 요청한 merchant_uid. imp_uid와 merchant_uid 중 하나는 필수어야합니다. 두 값이 모두 넘어오면 imp_uid를 우선 적용합니다.

        Returns:
            dict
        """
        api_instance = Payments(**self._api_kwargs)
        if imp_uid:
            response = api_instance.get(imp_uid)
        elif merchant_uid:
            response = api_instance.get_find(merchant_uid)
        else:
            raise KeyError('imp_uid와 merchant_uid 중 하나를 반드시 지정해야합니다.')

        return self._process_response(response)

    def cancel_payment(self, imp_uid=None, merchant_uid=None, amount=None, tax_free=None, reason=None):
        """승인된 결제를 취소합니다.

        Args:
            imp_uid (str): 아임포트 고유 번호
            merchant_uid (str): 가맹점지정 고유 번호. imp_uid와 merchant_uid 중 하나는 필수이어야합니다. 두 값이 모두 넘어오면 imp_uid를 우선 적용합니다.
            amount (float): 취소 요청 금액. 누락 시 전액을 취소합니다.
            tax_free (float): 취소 요청 금액 중 면세 금액. 누락 시 0원으로 간주합니다.
            reason (str): 취소 사유

        Returns:
            dict
        """
        if not (imp_uid or merchant_uid):
            raise KeyError('imp_uid와 merchant_uid 중 하나를 반드시 지정해야합니다.')

        api_instance = Payments(**self._api_kwargs)
        response = api_instance.post_cancel(imp_uid=imp_uid, merchant_uid=merchant_uid,
                                            amount=amount, tax_free=tax_free,
                                            reason=reason, )

        return self._process_response(response)

    def create_billkey(self, customer_uid=None, card_number=None, expiry=None, birth=None, pwd_2dight=None, pg=None,
                       customer_info=None):
        """정기결제 등에 사용하는 비인증결제를 위한 빌링키를 발급합니다.

        Args:
            customer_uid (str): 구매자 고유 번호
            card_number (str): 카드번호 (dddd-dddd-dddd-dddd)
            expiry (str): 카드 유효기간 (YYYY-MM)
            birth (str): 생년월일6자리 (법인카드의 경우 사업자등록번호10자리)
            pwd_2dight (str): 카드비밀번호 앞 2자리 (법인카드의 경우 생략가능)
            pg (str): API 방식 비인증 PG설정이 2개 이상인 경우, 결제가 진행되길 원하는 PG사를 지정하실 수 있습니다.
            customer_info (dict): 고객(카드소지자) 정보 (name, tel, email, addr, postcode)

        Returns:
            dict
        """
        if not (customer_uid and card_number and expiry and birth):
            raise KeyError('customer_uid, card_number, expiry, birth는 필수값입니다.')
        if not customer_info:
            customer_info = {}

        api_instance = Subscribe(**self._api_kwargs)
        response = api_instance.post_customers(customer_uid, card_number, expiry, birth, pwd_2dight=pwd_2dight, pg=pg,
                                               customer_name=customer_info.get('name'),
                                               customer_tel=customer_info.get('tel'),
                                               customer_email=customer_info.get('email'),
                                               customer_addr=customer_info.get('addr'),
                                               customer_postcode=customer_info.get('postcode'))

        return self._process_response(response)

    def find_billkey(self, customer_uid=None):
        """빌링키 정보를 조회합니다

        Args:
            customer_uid (str): 구매자 고유번호

        Returns:
            dict
        """
        if not customer_uid:
            raise KeyError('customer_uid는 필수값입니다.')

        api_instance = Subscribe(**self._api_kwargs)
        response = api_instance.get_customers(customer_uid)

        return self._process_response(response)

    def delete_billkey(self, customer_uid=None):
        """빌링키를 삭제합니다

        Args:
            customer_uid (str): 구매자 고유번호

        Returns:
            dict
        """
        if not customer_uid:
            raise KeyError('customer_uid는 필수값입니다.')

        api_instance = Subscribe(**self._api_kwargs)
        response = api_instance.delete_customers(customer_uid)

        return self._process_response(response)

    def create_payment(self, merchant_uid=None, customer_uid=None, name=None, amount=None, vat=None,
                       card_number=None, expiry=None, birth=None, pwd_2dight=None, pg=None,
                       buyer_info=None, card_quota=None, custom_data=None):
        """카드정보 또는 빌링키로 결제를 요청합니다
        카드정보를 지정하여 일회성 키인 결제를 요청할 수 있으며, 빌링키(customer_uid)를 지정해 재결제를 요청할 수 있습니다.
        카드정보와 빌링키가 모두 지정되면 일회성 결제 수행 후 해당 카드정보를 바탕으로 빌링키를 저장합니다.

        Args:
            merchant_uid (str): 가맹점 거래 고유번호
            customer_uid (str): string 타입의 고객 고유번호
            name (str): 주문명
            amount (float): 결제금액
            vat (float): 결제금액 중 부가세 금액 (파라메터가 누락되면 10%로 자동 계산됨)
            card_number (str): 카드번호 (dddd-dddd-dddd-dddd)
            expiry (str): 카드 유효기간 (YYYY-MM)
            birth (str): 생년월일6자리 (법인카드의 경우 사업자등록번호10자리)
            pwd_2dight (str): 카드비밀번호 앞 2자리 (법인카드의 경우 생략가능)
            pg (str): API 방식 비인증 PG설정이 2개 이상인 경우, 결제가 진행되길 원하는 PG사를 지정하실 수 있습니다.
            buyer_info (dict): 구매자 정보 (name, tel, email, addr, postcode)
            card_quota (int): 카드할부개월수. 2 이상의 integer 할부개월수 적용 (결제금액 50,000원 이상 한정)
            custom_data (str): 거래정보와 함께 저장할 추가 정보

        Returns:
            dict
        """
        if not (merchant_uid and name and amount):
            raise KeyError('merchant_uid, name, amount는 필수값입니다.')
        if not ((card_number and expiry and birth) or customer_uid):
            raise KeyError('카드 정보 또는 customer_uid 중 하나 이상은 반드시 포함되어야합니다.')
        if not buyer_info:
            buyer_info = {}

        api_instance = Subscribe(**self._api_kwargs)
        if card_number and expiry and birth:
            response = api_instance.post_payments_onetime(merchant_uid, amount, card_number, expiry, birth,
                                                          pwd_2dight=pwd_2dight, vat=vat, customer_uid=customer_uid,
                                                          pg=pg, name=name,
                                                          buyer_name=buyer_info.get('name'),
                                                          buyer_email=buyer_info.get('email'),
                                                          buyer_tel=buyer_info.get('tel'),
                                                          buyer_addr=buyer_info.get('addr'),
                                                          buyer_postcode=buyer_info.get('postcode'),
                                                          card_quota=card_quota, custom_data=custom_data)
        else:
            response = api_instance.post_payments_again(customer_uid, merchant_uid, amount, name, vat=vat,
                                                        buyer_name=buyer_info.get('name'),
                                                        buyer_email=buyer_info.get('email'),
                                                        buyer_tel=buyer_info.get('tel'),
                                                        buyer_addr=buyer_info.get('addr'),
                                                        buyer_postcode=buyer_info.get('postcode'),
                                                        card_quota=card_quota,
                                                        custom_data=custom_data)

        return self._process_response(response)
