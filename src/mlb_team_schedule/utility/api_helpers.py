import requests


def fetch(url):
    print(f"Fetching a response from {url}")

    response = requests.get(url)

    if response.status_code == 200:
        print(f"Received a response from {url}", "Sending back JSON")
        return response.json()
    elif 400 <= response.status_code <= 499:
        raise ClientErrorStatusCodeException(
            f"When Fetching from {url}: Got a {response.status_code} Client Error Code"
        )
    elif 500 <= response.status_code <= 599:
        raise ServerErrorStatusCodeException(
            f"When Fetching from {url}: Got a {response.status_code} Server Error Code"
        )
    else:
        raise UnexpectedHttpResponseStatusCodeException(
            f"When Fetching from {url}: Got a {response.status_code} Status Code"
        )


#! Status Code Exceptions
class UnexpectedHttpResponseStatusCodeException(Exception):
    """Raise when encountering an unexpected status code that is not between 400 and 599

    If the status code is 400-499, use the ClientError Exception subclass.
    If the status code is 500-599, use the ServerError Exception subclass.
    """

class ClientErrorStatusCodeException(UnexpectedHttpResponseStatusCodeException):
    """Raise when receiving HTTP Responses that have a 400-499 status code"""

class ServerErrorStatusCodeException(UnexpectedHttpResponseStatusCodeException):
    """Raise when receiving HTTP Responses that have a 500-599 status code"""

