class ImpApiError(Exception):
    def __init__(self, response):
        self.response = response

    def __str__(self):
        return "아임포트 API 오류 (status={status}, message={message})".format(
            status=self.response.status, message=self.response.message
        )


class ImpUnAuthorized(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "아임포트 인증 실패 (message={message})".format(message=self.message)
