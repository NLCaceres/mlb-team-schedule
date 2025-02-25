"""Useful for mocking out the `requests` library's get() and json() funcs"""


class MockHttpResponse:
    def __init__(self, status_code, jsonResponse=None):
        self.status_code = status_code
        #? Name MUST be "jsonResponse" or Python confuses the method & prop
        self.jsonResponse = jsonResponse or {}

    #? Passing `self` in json() def makes it an instance method, similar to other
    #? languages that implicitly get a reference to `self`/`this`
    def json(self):  #? Alternatively @staticmethod can make `java` style static funcs
        return self.jsonResponse

