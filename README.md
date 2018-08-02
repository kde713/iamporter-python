# iamporter-python
🚀 An I'mport REST API client for Human

[![CodeFactor](https://www.codefactor.io/repository/github/kde713/iamporter-python/badge)](https://www.codefactor.io/repository/github/kde713/iamporter-python)
![License](https://img.shields.io/github/license/kde713/iamporter-python.svg)

**iamporter-python** 는 [아임포트](https://www.iamport.kr/)에서 제공하는 REST API를 쉽게 활용하기 위해 작성된 Python 클라이언트입니다.

-----

### Why iamporter-python?

- 실제 프로덕션 서비스에 적용하기 위해 개발된 프로젝트입니다.
- Wrapping한 메소드가 구현되지 않은 경우라도 쉽게 아임포트 API를 요청할 수 있습니다.
- Docstring이 작성되어 있어 PyCharm과 같은 IDE에서 자동완성을 사용할 때 더욱 편리합니다.


### Disclaimer

- 이용 중 발생한 문제에 대하여 책임을 지지 않습니다. 단, Issue에 `help-wanted` 로 남겨주시면 도움을 드리기 위해 노력하겠습니다.
- Python 2를 지원하지 않습니다.


### Installation
 
```bash
pip install git+https://github.com/kde713/iamporter-python
```


### Quick Start

##### `Iamporter` 객체 활용 (General Way)

```python
from iamporter import Iamporter
from iamporter.errors import ImpUnAuthorized, ImpApiError


client = Iamporter(imp_key="YOUR_IAMPORT_REST_API_KEY", imp_secret="YOUR_IAMPORT_REST_API_SECRET")

try:
    client.find_payment(imp_uid="your_imp_uid")  # 아임포트 고유번호로 결제내역 조회
    client.find_payment(merchant_uid="your_merchant_uid")  # 가맹점지정 고유번호로 결제내역 조회
except KeyError:
    pass  # 필수값이 지정되지 않음
except ImpUnAuthorized as e:
    print(e.message)  # 아임포트 인증 실패 (인증 정보 오류)
except ImpApiError as e:
    print(e.response.status)  # API가 OK를 반환하지 않음 (API 오류)
    print(e.response.code)  # response 필드를 통해 API Response에 액세스 가능 (IamportResponse) 
    print(e.response.message)
    print(e.response.raw)

client.cancel_payment(imp_uid="your_imp_uid", reason="결제 취소 사유")  # 아임포트 고유번호로 승인된 결제 취소
client.cancel_payment(merchant_uid="your_merchant_uid", amount=10000, tax_free=5000)  # 가맹점지정 고유번호로 승인된 결제 취소
```

##### API 객체 활용 (Alternative Way)

```python
from iamporter import IamportAuth
from iamporter import api as iamport_api


auth = IamportAuth(imp_key="YOUR_IAMPORT_REST_API_KEY", imp_secret="YOUR_IAMPORT_REST_API_SECRET")

# /payments API
# Naming Eg: GET /payments/findAll 이라면 Payments.get_findall
payment_api = iamport_api.Payments(auth)
response = payment_api.get_find(merchant_uid="your_merchant_uid")  # API 객체의 모든 반환값은 IamportResponse 입니다.
print(response.raw)  # raw 프로퍼티로 원본 응답을 dict로 가져올 수 있습니다.
print(response.is_succeed)  # is_succeed 프로퍼티로 API 결과를 확인 가능합니다. Iamporter 객체와 달리 API 응답이 OK가 아니어도 Exception 이 발생하지 않습니다.

# 추가되지 않은 API
# 아직 추가되지 않은 API는 API 객체의 private method를 통해 쉽게 호출가능합니다. 이 메소드의 반환값 역시 IamportResponse 입니다.
response = payment_api._post('/payments/prepare', merchant_uid="your_merchant_uid", amount=5000)
response = payment_api._get('/payments/prepare/your_merchant_uid')
```