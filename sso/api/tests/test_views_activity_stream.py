import datetime

import mohawk
import pytest
from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

WHITELISTED_X_FORWARDED_FOR_HEADER = '1.2.3.4, ' + '4.5.5.5, ' + '3.5.5.5, ' + '2.5.5.5, ' + '1.5.5.5'


@pytest.fixture
def api_client():
    return APIClient()


def _url():
    return 'http://testserver' + reverse('api:activity-stream')


def _url_incorrect_domain():
    return 'http://incorrect' + reverse('api:activity-stream')


def _url_incorrect_path():
    return 'http://testserver' + reverse('api:activity-stream') + 'incorrect/'


def _auth_sender(key_id='some-id', secret_key='some-secret', url=_url, method='GET', content='', content_type=''):
    credentials = {
        'id': key_id,
        'key': secret_key,
        'algorithm': 'sha256',
    }
    return mohawk.Sender(
        credentials,
        url(),
        method,
        content=content,
        content_type=content_type,
    )


@pytest.mark.parametrize(
    'get_kwargs,expected_json',
    (
        (
            # If no X-Forwarded-For header
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender().request_header,
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If fifth-to-last X-Forwarded-For header isn't whitelisted
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender().request_header,
                HTTP_X_FORWARDED_FOR='6.6.6.6, ' + '7.7.7.7, ' + '8.8.8.8, ' + '9.9.9.9, ' + '123.123.123.123',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the only IP address in X-Forwarded-For is whitelisted
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender().request_header,
                HTTP_X_FORWARDED_FOR='1.2.3.4',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the only IP address in X-Forwarded-For isn't whitelisted
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender().request_header,
                HTTP_X_FORWARDED_FOR='123.123.123.123',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If sixth-to-last IP in X-Forwarded-For header is whitelisted
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender().request_header,
                HTTP_X_FORWARDED_FOR='1.2.3.4, '
                + '2.2.2.2, '
                + '7.7.7.7, '
                + '8.8.8.8, '
                + '9.9.9.9, '
                + '123.123.123.123',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If last of 5 IPs in X-Forwarded-For header is whitelisted
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender().request_header,
                HTTP_X_FORWARDED_FOR='6.6.6.6, ' + '7.7.7.7, ' + '8.8.8.8, ' + '9.9.9.9, ' + '1.2.3.4',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header isn't passed
            dict(
                content_type='',
                HTTP_X_FORWARDED_FOR=WHITELISTED_X_FORWARDED_FOR_HEADER,
            ),
            {'detail': 'Authentication credentials were not provided.'},
        ),
        (
            # If the Authorization header generated from an incorrect ID
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender(
                    key_id='incorrect',
                ).request_header,
                HTTP_X_FORWARDED_FOR=WHITELISTED_X_FORWARDED_FOR_HEADER,
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from an incorrect secret
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender(secret_key='incorrect').request_header,
                HTTP_X_FORWARDED_FOR=WHITELISTED_X_FORWARDED_FOR_HEADER,
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from an incorrect domain
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender(
                    url=_url_incorrect_domain,
                ).request_header,
                HTTP_X_FORWARDED_FOR=WHITELISTED_X_FORWARDED_FOR_HEADER,
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from an incorrect path
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender(
                    url=_url_incorrect_path,
                ).request_header,
                HTTP_X_FORWARDED_FOR=WHITELISTED_X_FORWARDED_FOR_HEADER,
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from an incorrect method
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender(
                    method='POST',
                ).request_header,
                HTTP_X_FORWARDED_FOR=WHITELISTED_X_FORWARDED_FOR_HEADER,
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from an incorrect
            # content-type
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender(
                    content_type='incorrect',
                ).request_header,
                HTTP_X_FORWARDED_FOR=WHITELISTED_X_FORWARDED_FOR_HEADER,
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from incorrect content
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender(
                    content='incorrect',
                ).request_header,
                HTTP_X_FORWARDED_FOR=WHITELISTED_X_FORWARDED_FOR_HEADER,
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
    ),
)
@pytest.mark.django_db
def test_401_returned(api_client, get_kwargs, expected_json):
    """If the request isn't properly Hawk-authenticated, then a 401 is
    returned
    """
    response = api_client.get(
        _url(),
        **get_kwargs,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == expected_json


@pytest.mark.django_db
def test_if_61_seconds_in_past_401_returned(api_client):
    """If the Authorization header is generated 61 seconds in the past, then a
    401 is returned
    """
    past = datetime.datetime.now() - datetime.timedelta(seconds=61)
    with freeze_time(past):
        auth = _auth_sender().request_header
    response = api_client.get(
        reverse('api:activity-stream'),
        content_type='',
        HTTP_AUTHORIZATION=auth,
        HTTP_X_FORWARDED_FOR=WHITELISTED_X_FORWARDED_FOR_HEADER,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error = {'detail': 'Incorrect authentication credentials.'}
    assert response.json() == error


@pytest.mark.django_db
def test_empty_object_returned_with_authentication_3_ips(api_client):
    """If the Authorization and X-Forwarded-For headers are correct,
    with an extra IP address prepended to the X-Forwarded-For then
    the correct, and authentic, data is returned
    """
    sender = _auth_sender()
    response = api_client.get(
        _url(),
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
        HTTP_X_FORWARDED_FOR=f'3.3.3.3, {WHITELISTED_X_FORWARDED_FOR_HEADER}',
    )

    assert response.status_code == status.HTTP_200_OK
    content = {'secret': 'content-for-pen-test'}
    assert response.json() == content


@pytest.mark.django_db
def test_empty_object_returned_with_authentication(api_client):
    """If the Authorization and X-Forwarded-For headers are correct, then
    the correct, and authentic, data is returned
    """
    sender = _auth_sender()
    response = api_client.get(
        _url(),
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
        HTTP_X_FORWARDED_FOR=WHITELISTED_X_FORWARDED_FOR_HEADER,
    )

    assert response.status_code == status.HTTP_200_OK
    content = {'secret': 'content-for-pen-test'}
    assert response.json() == content

    # Just asserting that accept_response doesn't raise is a bit weak,
    # so we also assert that it raises if the header, content, or
    # content_type are incorrect
    sender.accept_response(
        response_header=response['Server-Authorization'],
        content=response.content,
        content_type=response['Content-Type'],
    )
    with pytest.raises(mohawk.exc.MacMismatch):
        sender.accept_response(
            response_header=response['Server-Authorization'] + 'incorrect',
            content=response.content,
            content_type=response['Content-Type'],
        )
    with pytest.raises(mohawk.exc.MisComputedContentHash):
        sender.accept_response(
            response_header=response['Server-Authorization'],
            content='incorrect',
            content_type=response['Content-Type'],
        )
    with pytest.raises(mohawk.exc.MisComputedContentHash):
        sender.accept_response(
            response_header=response['Server-Authorization'],
            content=response.content,
            content_type='incorrect',
        )
