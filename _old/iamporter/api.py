from .base import IamportResponse, BaseApi


class Certifications(BaseApi):
    NAMESPACE = "certifications"


class Cards(BaseApi):
    NAMESPACE = "cards"


class Banks(BaseApi):
    NAMESPACE = "banks"


class Escrows(BaseApi):
    NAMESPACE = "escrows"


class Naver(BaseApi):
    NAMESPACE = "naver"


class Payco(BaseApi):
    NAMESPACE = "payco"


class Payments(BaseApi):
    NAMESPACE = "payments"

    def get_balance(self, imp_uid):
        """결제수단별 금액 상세 정보 확인
        아임포트 고유번호로 결제수단별 금액 상세정보를 확인합니다.(현재, PAYCO결제수단에 한해 제공되고 있습니다.)

        Args:
            imp_uid (str): 아임포트 고유번호

        Returns:
            IamportResponse
        """
        return self._get('/{imp_uid}/balance'.format(imp_uid=imp_uid))

    def get(self, imp_uid):
        """아임포트 고유번호로 결제내역을 확인합니다

        Args:
            imp_uid (str): 아임포트 고유번호

        Returns:
            IamportResponse
        """
        return self._get('/{imp_uid}'.format(imp_uid=imp_uid))

    def get_find(self, merchant_uid, payment_status=None, sorting=None):
        """가맹점지정 고유번호로 결제내역을 확인합니다
        동일한 merchant_uid가 여러 건 존재하는 경우, 정렬 기준에 따라 가장 첫 번째 해당되는 건을 반환합니다.
        (모든 내역에 대한 조회가 필요하시면 get_findall을 사용해주세요.)

        Args:
            merchant_uid (str): 결제요청 시 가맹점에서 요청한 merchant_uid
            payment_status (str): 특정 status상태의 값만 필터링하고 싶은 경우에 사용. 지정하지 않으면 모든 상태를 대상으로 조회합니다.
            sorting (str): 정렬기준. 기본값은 -started.

        Returns:
            IamportResponse
        """
        payment_status = "/" + payment_status if payment_status else ""
        params = self._build_params(sorting=sorting)
        return self._get('/find/{merchant_uid}{payment_status}'.format(merchant_uid=merchant_uid,
                                                                       payment_status=payment_status),
                         **params)

    def get_findall(self, merchant_uid, payment_status=None, page=None, sorting=None):
        """가맹점지정 고유번호로 결제내역을 확인합니다

        Args:
            merchant_uid (str): 결제요청 시 가맹점에서 요청한 merchant_uid
            payment_status (str): 특정 status상태의 값만 필터링하고 싶은 경우에 사용. 지정하지 않으면 모든 상태를 대상으로 조회합니다.
            page (int): 1부터 시작. 기본값 1
            sorting (str): 정렬기준. 기본값은 -started.

        Returns:
            IamportResponse
        """
        payment_status = "/" + payment_status if payment_status else ""
        params = self._build_params(page=page, sorting=sorting)
        return self._get('/findAll/{merchant_uid}{payment_status}'.format(merchant_uid=merchant_uid,
                                                                          payment_status=payment_status),
                         **params)

    def get_status(self, payment_status, page=None, limit=None, search_from=None, search_to=None, sorting=None):
        """미결제/결제완료/결제취소/결제실패 상태 별로 검색(20건씩 최신순 페이징)
        미결제/결제완료/결제취소/결제실패 상태 별로 검색할 수 있습니다.(20건씩 최신순 페이징)
        검색기간은 최대 90일까지이며 to파라메터의 기본값은 현재 unix timestamp이고 from파라메터의 기본값은 to파라메터 기준으로 90일 전입니다. 때문에, from/to 파라메터가 없이 호출되면 현재 시점 기준으로 최근 90일 구간에 대한 데이터를 검색하게 됩니다.
        from, to 파라메터를 지정하여 90일 단위로 과거 데이터 조회는 가능합니다.

        Args:
            payment_status (str)
            page (int): 1부터 시작. 기본값 1
            limit (int): 한 번에 조회할 결제건수.(최대 100건, 기본값 20건)
            search_from (int): 시간별 검색 시작 시각(>=) UNIX TIMESTAMP. 결제건의 최종 status에 따라 다른 검색기준이 적용됩니다. 기본값은 to 파라메터 기준으로 90일 전 unix timestamp.
            search_to (int): 시간별 검색 종료 시각(<=) UNIX TIMESTAMP. 결제건의 최종 status에 따라 다른 검색기준이 적용됩니다. 기본값은 현재 unix timestamp.
            sorting (str): 정렬기준. 기본값은 -started

        Returns:
            IamportResponse
        """
        params = self._build_params(
            **{'page': page, 'limit': limit, 'from': search_from, 'to': search_to, 'sorting': sorting})
        return self._get('/status/{payment_status}'.format(payment_status=payment_status), **params)

    def post_cancel(self, imp_uid=None, merchant_uid=None, amount=None, tax_free=None, checksum=None, reason=None,
                    refund_holder=None, refund_bank=None, refund_account=None):
        """승인된 결제를 취소합니다.
        신용카드/실시간계좌이체/휴대폰소액결제의 경우 즉시 취소처리가 이뤄지게 되며, 가상계좌의 경우는 환불받으실 계좌정보를 같이 전달해주시면 환불정보가 PG사에 등록되어 익영업일에 처리됩니다.(가상계좌 환불관련 특약계약 필요)

        Args:
            imp_uid (str): 취소할 거래의 아임포트 고유번호
            merchant_uid (str): 가맹점에서 전달한 거래 고유번호. imp_uid, merchant_uid 중 하나는 필수이어야 합니다. 두 값이 모두 넘어오면 imp_uid를 우선 적용합니다.
            amount (float): (부분)취소요청금액(누락이면 전액취소)
            tax_free (float): (부분)취소요청금액 중 면세금액(누락되면 0원처리)
            checksum (float): 취소 트랜잭션 수행 전, 현재시점의 취소 가능한 잔액. 누락 시 검증 프로세스를 생략합니다.
            reason (str): 취소 사유
            refund_holder (str): 환불계좌 예금주(가상계좌취소시 필수)
            refund_bank (str): 환불계좌 은행코드(하단 은행코드표 참조, 가상계좌취소시 필수)
            refund_account (str): 환불계좌 계좌번호(가상계좌취소시 필수)

        Returns:
            IamportResponse
        """
        params = self._build_params(**{
            'imp_uid': imp_uid,
            'merchant_uid': merchant_uid,
            'amount': amount,
            'tax_free': tax_free,
            'checksum': checksum,
            'reason': reason,
            'refund_holder': refund_holder,
            'refund_bank': refund_bank,
            'refund_account': refund_account,
        })
        return self._post('/cancel', **params)


class Receipts(BaseApi):
    NAMESPACE = "receipts"


class Subscribe(BaseApi):
    NAMESPACE = "subscribe"

    def get_customers(self, customer_uid):
        """구매자의 빌링키 정보 조회

        Args:
            customer_uid (str): 구매자 고유 번호

        Returns:
            IamportResponse
        """
        return self._get('/customers/{customer_uid}'.format(customer_uid=customer_uid))

    def post_customers(self, customer_uid, card_number, expiry, birth, pwd_2digit=None, pg=None,
                       customer_name=None, customer_tel=None, customer_email=None, customer_addr=None,
                       customer_postcode=None):
        """구매자에 대해 빌링키 발급 및 저장

        Args:
            customer_uid (str): 구매자 고유 번호
            card_number (str): 카드번호 (dddd-dddd-dddd-dddd)
            expiry (str): 카드 유효기간 (YYYY-MM)
            birth (str): 생년월일6자리 (법인카드의 경우 사업자등록번호10자리)
            pwd_2digit (str): 카드비밀번호 앞 2자리 (법인카드의 경우 생략가능)
            pg (str): API 방식 비인증 PG설정이 2개 이상인 경우, 결제가 진행되길 원하는 PG사를 지정하실 수 있습니다.
            customer_name (str): 고객(카드소지자) 관리용 성함
            customer_tel (str): 고객(카드소지자) 전화번호
            customer_email (str): 고객(카드소지자) Email
            customer_addr (str): 고객(카드소지자) 주소
            customer_postcode (str): 고객(카드소지자) 우편번호

        Returns:
            IamportResponse
        """
        params = self._build_params(**{
            'card_number': card_number,
            'expiry': expiry,
            'birth': birth,
            'pwd_2digit': pwd_2digit,
            'pg': pg,
            'customer_name': customer_name,
            'customer_tel': customer_tel,
            'customer_email': customer_email,
            'customer_addr': customer_addr,
            'customer_postcode': customer_postcode,
        })
        return self._post('/customers/{customer_uid}'.format(customer_uid=customer_uid), **params)

    def delete_customers(self, customer_uid):
        """구매자의 빌링키 정보 삭제(DB에서 빌링키를 삭제[delete] 합니다)

        Args:
            customer_uid (str): 구매자 고유 번호

        Returns:
            IamportResponse
        """
        return self._delete('/customers/{customer_uid}'.format(customer_uid=customer_uid))

    def get_customers_payments(self, customer_uid, page=None):
        """구매자의 빌링키로 결제된 결제목록 조회

        Args:
            customer_uid (str): 구매자 고유번
            page (int): 페이징 페이지. 1부터 시작

        Returns:
            IamportResponse
        """
        params = self._build_params(page=page)
        return self._get('/customers/{customer_uid}/payments'.format(customer_uid=customer_uid), **params)

    def post_payments_onetime(self, merchant_uid, amount, card_number, expiry, birth=None, pwd_2digit=None,
                              vat=None, customer_uid=None, pg=None, name=None,
                              buyer_name=None, buyer_email=None, buyer_tel=None, buyer_addr=None, buyer_postcode=None,
                              card_quota=None, custom_data=None):
        """구매자로부터 별도의 인증과정을 거치지 않고, 카드정보만으로 결제를 진행하는 API
        customer_uid를 전달해주시면 결제 후 다음 번 결제를 위해 성공된 결제에 사용된 빌링키를 저장해두게되고, customer_uid가 없는 경우 저장되지 않습니다.
        동일한 merchant_uid는 재사용이 불가능하며 고유한 값을 전달해주셔야 합니다.
        빌링키 저장 시, buyer_email, buyer_name 등의 정보는 customer 부가정보인 customer_email, customer_name 등으로 함께 저장됩니다.
        .post_customers 참조

        Args:
            merchant_uid (str): 가맹점 거래 고유번호
            amount (float): 결제금액
            card_number (str): 카드번호 (dddd-dddd-dddd-dddd)
            expiry (str): 카드 유효기간 (YYYY-MM)
            birth (str): 생년월일6자리 (법인카드의 경우 사업자등록번호10자리)
            pwd_2digit (str): 카드비밀번호 앞 2자리 (법인카드의 경우 생략가능)
            vat (float): 결제금액 중 부가세 금액 (파라메터가 누락되면 10%로 자동 계산됨)
            customer_uid (str): string 타입의 고객 고유번호.
            pg (str): API 방식 비인증 PG설정이 2개 이상인 경우, 결제가 진행되길 원하는 PG사를 지정하실 수 있습니다.
            name (str): 주문명
            buyer_name (str): 주문자명
            buyer_email (str): 주문자 E-mail주소
            buyer_tel (str): 주문자 전화번호
            buyer_addr (str): 주문자 주소
            buyer_postcode (str): 주문자 우편번
            card_quota (int): 카드할부개월수. 2 이상의 integer 할부개월수 적용 (결제금액 50,000원 이상 한정)
            custom_data (str): 거래정보와 함께 저장할 추가 정보

        Returns:
            IamportResponse
        """
        params = self._build_params(**{
            'merchant_uid': merchant_uid,
            'amount': amount,
            'card_number': card_number,
            'expiry': expiry,
            'birth': birth,
            'pwd_2digit': pwd_2digit,
            'vat': vat,
            'customer_uid': customer_uid,
            'pg': pg,
            'name': name,
            'buyer_name': buyer_name,
            'buyer_email': buyer_email,
            'buyer_tel': buyer_tel,
            'buyer_addr': buyer_addr,
            'buyer_postcode': buyer_postcode,
            'card_quota': card_quota,
            'custom_data': custom_data,
        })
        return self._post('/payments/onetime', **params)

    def post_payments_again(self, customer_uid, merchant_uid, amount, name, vat=None,
                            buyer_name=None, buyer_email=None, buyer_tel=None, buyer_addr=None, buyer_postcode=None,
                            card_quota=None, custom_data=None):
        """저장된 빌링키로 재결제를 하는 경우 사용됩니다.
        .post_payments_onetime 또는 Subscribe.post_customers 로 등록된 빌링키가 있을 때 매칭되는 customer_uid로 재결제를 진행할 수 있습니다.

        Args:
            customer_uid (str): string 타입의 고객 고유번호
            merchant_uid (str): 가맹점 거래 고유번호
            amount (float): 결제금액
            name (str): 주문명
            vat (float): 결제금액 중 부가세 금액(파라메터가 누락되면 10%로 자동 계산됨)
            buyer_name (str): 주문자명
            buyer_email (str): 주문자 E-mail주소
            buyer_tel (str): 주문자 전화번호
            buyer_addr (str): 주문자 주소
            buyer_postcode (str): 주문자 우편번
            card_quota (int): 카드할부개월수. 2 이상의 integer 할부개월수 적용 (결제금액 50,000원 이상 한정)
            custom_data (str): 거래정보와 함께 저장할 추가 정보

        Returns:
            IamportResponse
        """
        params = self._build_params(**{
            'customer_uid': customer_uid,
            'merchant_uid': merchant_uid,
            'amount': amount,
            'name': name,
            'vat': vat,
            'buyer_name': buyer_name,
            'buyer_email': buyer_email,
            'buyer_tel': buyer_tel,
            'buyer_addr': buyer_addr,
            'buyer_postcode': buyer_postcode,
            'card_quota': card_quota,
            'custom_data': custom_data,
        })
        return self._post('/payments/again', **params)


class VBanks(BaseApi):
    NAMESPACE = "vbanks"
