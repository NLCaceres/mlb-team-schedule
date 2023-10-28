import requests


def fetch(url):
    print(f"Fetching a response from {url}")
    
    response = requests.get(url)

    if response.status_code == 200:
        print(f"Received a response from {url}", "Sending back JSON")
        return response.json()
    elif 400 <= response.status_code <= 499:
        raise ClientErrorStatusCodeException(
            f"While Fetching from {url}: Found a {response.status_code} Client Error Status Code"
        )
    elif 500 <= response.status_code <= 599:
        raise ServerErrorStatusCodeException(
            f"While Fetching from {url}: Found a {response.status_code} Server Error Status Code"
        )
    else:
        raise UnexpectedHttpResponseStatusCodeException(
            f"While Fetching from {url}: Found an unexpected {response.status_code} Status Code"
        )


#! Status Code Exceptions
class UnexpectedHttpResponseStatusCodeException(Exception):
    """Raise when encountering an unexpected status code

    Use the ClientError and ServerError Exception subclasses for 400-499 and 500-599 status codes, respectively

    """

class ClientErrorStatusCodeException(UnexpectedHttpResponseStatusCodeException):
    """Raise when receiving HTTP Responses that have a 400-499 status code"""

class ServerErrorStatusCodeException(UnexpectedHttpResponseStatusCodeException):
    """Raise when receiving HTTP Responses that have a 500-599 status code"""