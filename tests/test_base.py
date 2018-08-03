import sys
import unittest

sys.path.append('..')
from tests import conftest
from iamporter import base, errors, consts


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

        self.valid_response1 = base.IamportResponse(self.VALID_RESPONSE1)
        self.invalid_response1 = base.IamportResponse(self.INVALID_RESPONSE1)
        self.invalid_response2 = base.IamportResponse(self.INVALID_RESPONSE2)

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
        self.assertRaises(errors.ImpUnAuthorized, base.IamportAuth, "invalid_key", "invalid_secret")

    def test_valid_auth(self):
        auth = base.IamportAuth(conftest.TEST_IMP_KEY, conftest.TEST_IMP_SECRET)
        self.assertTrue(auth.token)


class TestBaseApi(unittest.TestCase):
    def setUp(self):
        class SampleBaseApi(base.BaseApi):
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
