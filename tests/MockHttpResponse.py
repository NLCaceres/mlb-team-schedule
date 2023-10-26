#* Useful for mocking out the `requests` library's get() and json() funcs
class MockHttpResponse:
    def __init__(self, status_code, jsonResponse = None):
        self.status_code = status_code
        #? Needs to be named jsonResponse, not just json, or Python confuses the method and prop
        self.jsonResponse = jsonResponse or { }

    #? By passing self into the definition of json(), it becomes an instance method,
    #? similar in usage to other langs, where instances don't actually need to pass in self
    def json(self): #? Alternatively @staticmethod can be used instead of passing in self
        return self.jsonResponse