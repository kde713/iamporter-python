import sys
import unittest

sys.path.append('..')
from tests import conftest
from iamporter import Iamporter, IamportAuth, errors


class TestIamporter(unittest.TestCase):
    def setUp(self):
        self.imp_auth = IamportAuth(conftest.TEST_IMP_KEY, conftest.TEST_IMP_SECRET)
        self.client = Iamporter(imp_auth=self.imp_auth)

    def test_init(self):
        self.assertRaises(errors.ImpUnAuthorized, Iamporter, imp_key="invalid_key", imp_secret="invalid_secret")

    def test_find_payment(self):
        self.assertRaises(KeyError, self.client.find_payment)
        self.assertRaises(errors.ImpApiError, self.client.find_payment, imp_uid='test')
        self.assertRaises(errors.ImpApiError, self.client.find_payment, merchant_uid='âàáaā')

    def test_cancel_payment(self):
        self.assertRaises(errors.ImpApiError, self.client.cancel_payment, imp_uid='nothing', reason='reason')
        try:
            self.client.cancel_payment(imp_uid='nothing', reason='reason')
        except errors.ImpApiError as e:
            self.assertEqual(e.response.code, 1)
            self.assertEqual(e.response.message, '취소할 결제건이 존재하지 않습니다.')

        try:
            self.client.cancel_payment(merchant_uid='any-merchant_uid', reason='any-reason')
        except errors.ImpApiError as e:
            self.assertEqual(e.response.code, 1)
            self.assertEqual(e.response.message, '취소할 결제건이 존재하지 않습니다.')

        self.assertRaises(KeyError, self.client.cancel_payment, merchant_uid=None, reason='some-reason아 ')

    def test_cancel_payment_partital(self):
        try:
            self.client.cancel_payment(imp_uid='nothing', reason='reason', amount=100)
        except errors.ImpApiError as e:
            self.assertEqual(e.response.code, 1)
            self.assertEqual(e.response.message, '취소할 결제건이 존재하지 않습니다.')

    def test_create_billkey(self):
        self.assertRaises(KeyError, self.client.create_billkey,
                          customer_uid=None, card_number="0000-0000-0000-0000", expiry="2022-06", birth="960714")

        try:
            self.client.create_billkey(customer_uid="customer_1234", card_number="1111-1111-1111-1111",
                                       expiry="2022-06", birth="960714", pwd_2dight="12")
        except errors.ImpApiError as e:
            self.assertEqual(e.response.code, -1)
            self.assertIn("유효하지않은 카드번호를 입력하셨습니다.", e.response.message)

    def test_find_billkey(self):
        self.assertRaises(KeyError, self.client.find_billkey, customer_uid=None)

        try:
            self.client.find_billkey(customer_uid="invalid-uid")
        except errors.ImpApiError as e:
            self.assertEqual(e.response.code, 1)
            self.assertEqual(e.response.message, "요청하신 customer_uid(invalid-uid)로 등록된 정보를 찾을 수 없습니다.")

    def test_delete_billkey(self):
        self.assertRaises(KeyError, self.client.delete_billkey, customer_uid=None)

        try:
            self.client.delete_billkey(customer_uid="invalid-uid")
        except errors.ImpApiError as e:
            self.assertEqual(e.response.code, 1)
            self.assertEqual(e.response.message, "요청하신 customer_uid(invalid-uid)로 등록된 정보를 찾을 수 없습니다.")

    def test_create_payment_onetime(self):
        self.assertRaises(KeyError, self.client.create_payment, merchant_uid=None, name="테스트", amount=10000)
        self.assertRaises(KeyError, self.client.create_payment, merchant_uid='test', name="테스트", amount=10000,
                          card_number="1111-1111-1111-1111", expiry="2022-06")

        try:
            self.client.create_payment(merchant_uid='some-special-uid', amount=1000, name="테스트",
                                       card_number="1111-1111-1111-1111", expiry="2022-06", birth="960714")
        except errors.ImpApiError as e:
            self.assertEqual(e.response.code, -1)
            self.assertIn("유효하지않은 카드번호를 입력하셨습니다.", e.response.message)

    def test_create_payment_again(self):
        try:
            self.client.create_payment(merchant_uid='some-special-uid-2', amount=1000, name="테스트",
                                       customer_uid="invalid-uid", )
        except errors.ImpApiError as e:
            self.assertEqual(e.response.code, 1)
            self.assertEqual(e.response.message, "등록되지 않은 구매자입니다.")

    def tearDown(self):
        del self.imp_auth
        del self.client
