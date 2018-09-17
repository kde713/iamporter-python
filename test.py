import unittest

from iamporter import Iamporter, IamportAuth, IamportResponse, errors, consts
from iamporter.base import BaseApi, build_url

TEST_IMP_KEY = "imp_apikey"
TEST_IMP_SECRET = "ekKoeW8RyKuT0zgaZsUtXXTLQ4AhPFW3ZGseDA6bkA5lamv9OqDMnxyeB9wqOsuO9W3Mx9YSJ4dTqJ3f"


class TestUrlBuilder(unittest.TestCase):
    def test_build_url(self):
        self.assertEqual(build_url("https://www.test.com", "not_slashed/path"),
                         "https://www.test.com/not_slashed/path")
        self.assertEqual(build_url("http://www.slashed.host/", "also_slashed/path"),
                         "http://www.slashed.host/also_slashed/path")
        self.assertEqual(build_url("http://www.withport.com:12345", "not_slashed/path"),
                         "http://www.withport.com:12345/not_slashed/path")


class TestIamportResponse(unittest.TestCase):
    def setUp(self):
        class MockResponse:
            def __init__(self, status, response):
                self.status_code = status
                self.response_body = response

            def json(self):
                return self.response_body

        self.VALID_RESPONSE1 = MockResponse(200, {'code': 0, 'message': "가짜 성공 응답",
                                                  'response': {"sample": "sample_data"}})
        self.INVALID_RESPONSE1 = MockResponse(400, {'code': 1, 'message': "가짜 실패 응답", 'response': {}})
        self.INVALID_RESPONSE2 = MockResponse(200, {'code': 2, 'message': "가짜 실패 응답 2", 'response': {}})

        self.valid_response1 = IamportResponse(self.VALID_RESPONSE1)
        self.invalid_response1 = IamportResponse(self.INVALID_RESPONSE1)
        self.invalid_response2 = IamportResponse(self.INVALID_RESPONSE2)

    def test_parse(self):
        self.assertEqual(self.valid_response1.status, 200)
        self.assertEqual(self.valid_response1.code, 0)
        self.assertEqual(self.valid_response1.message, "가짜 성공 응답")
        self.assertEqual(self.valid_response1.data, {"sample": "sample_data"})

    def test_is_succeed(self):
        self.assertEqual(self.valid_response1.is_succeed, True)
        self.assertEqual(self.invalid_response1.is_succeed, False)
        self.assertEqual(self.invalid_response2.is_succeed, False)

    def test_raw(self):
        self.assertEqual(self.valid_response1.raw,
                         {'code': 0, 'message': "가짜 성공 응답", 'response': {"sample": "sample_data"}})


class TestIamportAuth(unittest.TestCase):
    def test_invalid_auth(self):
        self.assertRaises(errors.ImpUnAuthorized, IamportAuth, "invalid_key", "invalid_secret")

    def test_valid_auth(self):
        auth = IamportAuth(TEST_IMP_KEY, TEST_IMP_SECRET)
        self.assertTrue(auth.token)


class TestBaseApi(unittest.TestCase):
    def setUp(self):
        class SampleBaseApi(BaseApi):
            NAMESPACE = "sample"

        self.api_client = SampleBaseApi(None)  # BaseApi의 유틸성 메소드만 테스트할 것이기에 인증 과정을 bypass

    def test_build_url(self):
        self.assertEqual(self.api_client._build_url("/endpoint"), consts.IAMPORT_API_URL + "sample/endpoint")

    def test_build_params(self):
        MOCK_PARAMS = {
            'valid_param1': 123,
            'invalid_param1': None,
            'valid_param2': "",
        }
        built_params = self.api_client._build_params(**MOCK_PARAMS)
        self.assertIn('valid_param1', built_params.keys())
        self.assertNotIn('invalid_param1', built_params.keys())
        self.assertIn('valid_param2', built_params.keys())


class TestIamporter(unittest.TestCase):
    def setUp(self):
        self.imp_auth = IamportAuth(TEST_IMP_KEY, TEST_IMP_SECRET)
        self.client = Iamporter(imp_auth=self.imp_auth)

    def test_init(self):
        self.assertRaises(errors.ImpUnAuthorized, Iamporter, imp_key=None)
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


if __name__ == "__main__":
    unittest.main()
