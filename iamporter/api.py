from .base import IamportResponse, BaseApi

__all__ = ["Payments", ]


class Payments(BaseApi):
    def get_balance(self, imp_uid):
        """결제수단별 금액 상세 정보 확인
        아임포트 고유번호로 결제수단별 금액 상세정보를 확인합니다.(현재, PAYCO결제수단에 한해 제공되고 있습니다.)

        Args:
            imp_uid (str): 아임포트 고유번호

        Returns:
            IamportResponse
        """
        return self._get('/payments/{imp_uid}/balance'.format(imp_uid=imp_uid))

    def get(self, imp_uid):
        """아임포트 고유번호로 결제내역을 확인합니다

        Args:
            imp_uid (str): 아임포트 고유번호

        Returns:
            IamportResponse
        """
        return self._get('/payments/{imp_uid}'.format(imp_uid=imp_uid))

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
        return self._get('/payments/find/{merchant_uid}{payment_status}'.format(merchant_uid=merchant_uid,
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
        return self._get('/payments/findAll/{merchant_uid}{payment_status}'.format(merchant_uid=merchant_uid,
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
        return self._get('/payments/status/{payment_status}'.format(payment_status=payment_status), **params)

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
        return self._post('/payments/cancel', **params)
