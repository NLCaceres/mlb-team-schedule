from ..common_assertions import assertIsNotNone
from ..MockHttpResponse import MockHttpResponse
from mlb_team_schedule.utility.api_helpers import (
    ClientErrorStatusCodeException, ServerErrorStatusCodeException,
    UnexpectedHttpResponseStatusCodeException, fetch,
)

import pytest
import requests


def test_fetch(monkeypatch):
    mockResponse = MockHttpResponse(404)
    def mock_JSON(*args, **kwargs):
        return mockResponse
    monkeypatch.setattr(requests, "get", mock_JSON)

    #? Sanity check, Python lets funcs get called w/out args
    with pytest.raises(TypeError): # BUT will raise an error if wrong
        fetch()

    #* WHEN a status code in the 400s is found (from mockResponse above)
    with pytest.raises(ClientErrorStatusCodeException):
        fetch("/foobar") #* THEN ClientErrorStatusCodeException is raised

    #* WHEN a status code in the 500s is found
    mockResponse.status_code = 500 #? Internal Server Error
    with pytest.raises(ServerErrorStatusCodeException):
        fetch("/foobar") #* THEN ServerErrorStatusCodeException is raised

    #* WHEN a status code that is NOT 200 is found
    mockResponse.status_code = 301 #? Permanently moved
    with pytest.raises(UnexpectedHttpResponseStatusCodeException):
        fetch("/foobar") #* THEN raise a generic UnexpectedHttpResponseStatusCodeException
    mockResponse.status_code = 202 #? No Content
    with pytest.raises(UnexpectedHttpResponseStatusCodeException):
        fetch("/foobar") #* THEN raise a generic UnexpectedHttpResponseStatusCodeException

    #* WHEN a 200 status code is found
    mockResponse.status_code = 200
    mockResponse.jsonResponse = { "foo": "bar" }
    jsonResponse = fetch("/foobar") #* THEN the proper JSON response is received
    assertIsNotNone(jsonResponse)
    assert jsonResponse["foo"] == "bar"
