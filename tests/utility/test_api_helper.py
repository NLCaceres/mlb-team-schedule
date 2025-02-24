from mlb_team_schedule.utility.api_helpers import (fetch, ClientErrorStatusCodeException,
                                                   ServerErrorStatusCodeException, UnexpectedHttpResponseStatusCodeException)
import pytest
import requests
from ..common_assertions import assertIsNotNone
from ..MockHttpResponse import MockHttpResponse


def test_fetch(monkeypatch):
    mockResponse = MockHttpResponse(404)
    def mock_JSON(*args, **kwargs):
        return mockResponse
    monkeypatch.setattr(requests, "get", mock_JSON)

    #? Simple sanity check, Python may allow funcs to be called w/out their args BUT it'll raise a TypeError
    with pytest.raises(TypeError):
        fetch()

    #* WHEN a status code in the 400s is found
    with pytest.raises(ClientErrorStatusCodeException): #* Due to 404 being set in constructor above
        fetch('/foobar') #* THEN ClientErrorStatusCodeException is raised

    #* WHEN a status code in the 500s is found
    mockResponse.status_code = 500 #? Internal Server Error
    with pytest.raises(ServerErrorStatusCodeException):
        fetch('/foobar') #* THEN ServerErrorStatusCodeException is raised

    #* WHEN a status code that is NOT 200 is found
    mockResponse.status_code = 301 #? Permanently moved
    with pytest.raises(UnexpectedHttpResponseStatusCodeException):
        fetch('/foobar') #* THEN a generic UnexpectedHttpResponseStatusCodeException is raised
    mockResponse.status_code = 202 #? No Content
    with pytest.raises(UnexpectedHttpResponseStatusCodeException):
        fetch('/foobar') #* THEN a generic UnexpectedHttpResponseStatusCodeException is raised

    #* WHEN a 200 status code is found
    mockResponse.status_code = 200
    mockResponse.jsonResponse = { 'foo': 'bar' }
    jsonResponse = fetch('/foobar') #* THEN the proper JSON response is received
    assertIsNotNone(jsonResponse)
    assert jsonResponse['foo'] == 'bar'
