# iamporter-python
🚀 An I'mport REST API client for Human

[![CircleCI](https://img.shields.io/circleci/project/github/kde713/iamporter-python.svg?logo=circleci)](https://circleci.com/gh/kde713/iamporter-python)
[![CodeCov](https://img.shields.io/codecov/c/github/kde713/iamporter-python.svg)](https://codecov.io/gh/kde713/iamporter-python)
[![CodeFactor](https://www.codefactor.io/repository/github/kde713/iamporter-python/badge)](https://www.codefactor.io/repository/github/kde713/iamporter-python)
![License](https://img.shields.io/github/license/kde713/iamporter-python.svg?logo=github)

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
pip install iamporter
```



### Specification

##### iamporter.Iamporter

- **Succeed:** API 응답이 OK인 경우 Response Body 의 response 필드를 `dict` 타입으로 반환합니다.
- **Failed:** HTTP 응답 코드가 403인 경우 `ImpUnAuthorized`, 이외의 경우 `ImpApiError` Exception을 발생시킵니다.

##### iamporter.api

- API 결과와 관계없이 `IamportResponse` 인스턴스를 반환합니다.



### Usage (General Way)

REST API를 사용하기 편하게 Wrapping한 Iamporter 객체를 통해 라이브러리를 활용하는 일반적인 방법입니다.

##### 준비

사용하기 위해 객체를 초기화합니다. 
`imp_auth` 인자에 `IamportAuth` 인스턴스를 전달하여 객체를 초기화할 수도 있습니다.

```python
from iamporter import Iamporter

client = Iamporter(imp_key="YOUR_IAMPORT_REST_API_KEY", imp_secret="YOUR_IAMPORT_REST_API_SECRET")
```

##### 예외 처리

- 필수값이 누락된 경우 `KeyError` 예외가 발생합니다.
- 클라이언트 객체 초기화 시 인증정보가 올바르지 않은 경우나 API 응답 HTTP Status Code가 403 인 경우 `iamporter.errors.ImpUnAuthorized` 예외가 발생합니다.
- 이외에 API 응답이 OK가 아닌 경우 `iamporter.errors.ImpApiError` 예외가 발생합니다.
    * `.response` 필드에 API 응답이 `IamportResponse` 타입으로 담겨있습니다.

##### 결제 내역 조회

아임포트 고유번호 (`imp_uid`)나 가맹점지정 고유번호 (`merchant_uid`)를 이용해 결제 정보를 조회합니다.

```python
client.find_payment(imp_uid="your_imp_uid")
client.find_payment(merchant_uid="your_merchant_uid")
```

##### 결제 취소

결제를 취소합니다.
취소 사유(`reason`), 취소 요청 금액(`amount`), 취소 요청 금액 중 면세금액(`tax_free`) 값을 지정할 수 있습니다.

```python
client.cancel_payment(imp_uid="your_imp_uid")
client.cancel_payment(merchant_uid="your_merchant_uid", amount=10000, tax_free=5000)
```

##### 빌링키 발급

정기 결제 등에 사용할 수 있는 빌링키를 발급합니다.
PG사 코드(`pg`), 카드소유자 정보(`customer_info`)를 지정할 수 있습니다.

```python
client.create_billkey(
    customer_uid="your_customer_uid",
    card_number="1234-1234-1234-1234",
    expiry="2022-06",
    birth="960712",
    pwd_2dight="12",
    customer_info={
        'name': "소유자 이름",
        'tel': "01000000000",
        'email': "someone@example.com",
        'addr': "사는 곳 주소",
        'postcode': "00000",    
    },
)
```

##### 빌링키 조회

빌링키 등록 정보를 조회합니다.

```python
client.find_billkey(customer_uid="your_customer_uid")
```

##### 빌링키 삭제

빌링키 등록정보를 삭제합니다.

```python
client.delete_billkey(customer_uid="your_customer_uid")
```

##### 비인증 결제 요청

구매자로 부터 별도의 인증과정을 거치지 않고 신용카드 정보 또는 빌링키를 이용해 결제를 요청합니다.
카드정보를 지정한 경우 `customer_uid`를 함꼐 지정하면 해당 카드 정보로 결제 후 빌링키가 저장됩니다.

```python
from iamporter import Iamporter
client = Iamporter(imp_key="YOUR_IAMPORT_REST_API_KEY", imp_secret="YOUR_IAMPORT_REST_API_SECRET")
client.create_payment(
    merchant_uid="your_merchant_uid",
    name="주문명",
    amount=10000,
    card_number="1234-1234-1234-1234",
    expiry="2022-06",
    birth="960712",
    pwd_2dight="12",
    buyer_info={
        'name': "구매자 이름",
        'tel': "01000000000",
        'email': "someone@example.com",
        'addr': "사는 곳 주소",
        'postcode': "00000",    
    },
)
client.create_payment(
    merchant_uid="your_merchant_uid",
    customer_uid="your_customer_uid",
    name="주문명",
    amount=10000,
)
```



### Usage (Alternative Way)

Iamporter 객체에 wrapping 되어 있지 않은 API를 사용하거나, 직접 API-Level에서 개발을 하기 위해 사용하는 방법입니다.

##### 준비

사용하기 위해 인증객체를 만듭니다.

```python
from iamporter import IamportAuth

auth = IamportAuth(imp_key="YOUR_IAMPORT_REST_API_KEY", imp_secret="YOUR_IAMPORT_REST_API_SECRET")
```

##### API Method List

모든 API-Level Class 들은 `iamporter.api` 에 위치합니다. 아래는 어떤 방식으로 API 와 대응되는 Class와 method의 이름이 정해지는지에 대한 예입니다. (모든 대응 목록이 아닙니다.)

| API | Class | Method |
| :-: | :---: | ------ |
| `GET /payments/{imp_uid}/balance` | `Payments` | `get_balance` |
| `GET /payments/{imp_uid}` | `Payments` | `get` |
| `GET /payments/find/{merchant_uid}/{payment_status}` | `Payments` | `get_find` |
| `GET /payments/findAll/{merchant_uid}/{payment_status}` | `Payments` | `get_findall` |
| `POST /subscribe/payments/onetime` | `Subscribe` | `post_payments_onetime` |
| `POST /subscribe/payments/again` | `Subscribe` | `post_payments_again` |
| `DELETE /subscribe/customers/{customer_uid}` | `Subscribe` | `delete_customers` | 

##### 대응되는 Method가 추가되어 있는 API 호출

```python
from iamporter.api import Payments

api_instance = Payments(auth)
response = api_instance.get("your_imp_uid")
```

##### 대응되는 Method가 없는 API 호출

```python
from iamporter.api import Escrows

api_instance = Escrows(auth)
response = api_instance._post('/logis/{imp_uid}'.format(imp_uid="your_imp_uid"), sender="", receiver="", logis="")
```

##### 응답 처리

모든 API Level의 응답은 `IamportResponse` 인스턴스로 반환됩니다.

```python
response.status  # HTTP Status Code
response.code  # API 응답 code 필드
response.message  # API 응답 message 필드
response.data  # API 응답 response 필드
response.is_succeed  # API 결과 OK 여부
response.raw  # API 응답 원문 (dict)
```
