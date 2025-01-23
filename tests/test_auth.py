import pytest
from jwt.exceptions import ExpiredSignatureError
from pytest_mock import MockerFixture

from python_utils.auth import Auth, AuthException


@pytest.fixture
def auth():
    return Auth("secret_key", "public_key")


def test_invalid_token_data_keys():
    with pytest.raises(AuthException) as e:
        Auth("secret_key", "public_key", [])
    assert str(e.value) == "Invalid token data keys"


def test_validate_public_key(auth: Auth):
    auth.validate_public_key("public_key")


def test_validate_public_key_invalid(auth: Auth):
    with pytest.raises(AuthException) as e:
        auth.validate_public_key("invalid_public_key")
    assert str(e.value) == "Invalid public key"


def test_create_access_token(auth: Auth):
    token_data = {"username": "username"}
    access_token = auth.create_access_token(token_data)
    auth.validate_token(access_token)


def test_create_access_token_missing_data(auth: Auth):
    token_data = {}
    with pytest.raises(AuthException) as e:
        auth.create_access_token(token_data)
    assert str(e.value) == "Missing required data in token"


def test_create_refresh_token(auth: Auth):
    token_data = {"username": "username"}
    refresh_token = auth.create_refresh_token(token_data)
    auth.validate_token(refresh_token)


def test_create_refresh_token_missing_data(auth: Auth):
    token_data = {}
    with pytest.raises(AuthException) as e:
        auth.create_refresh_token(token_data)
    assert str(e.value) == "Missing required data in token"


def test_validate_token_expired(auth: Auth, mocker: MockerFixture):
    # I failed to reproduce token expiration error so let's mock it
    mocker.patch("python_utils.auth.decode", side_effect=ExpiredSignatureError)
    access_token = auth.create_access_token({"username": "username"})
    with pytest.raises(AuthException) as e:
        auth.validate_token(access_token)
    assert str(e.value) == "Token expired"


def test_validate_token_invalid(auth: Auth):
    with pytest.raises(AuthException) as e:
        auth.validate_token("invalid_token")
    assert str(e.value) == "Invalid token"


def test_refresh_access_token(auth: Auth):
    refresh_token = auth.create_refresh_token({"username": "username"})
    access_token = auth.refresh_access_token(refresh_token)
    auth.validate_token(access_token)


def test_refresh_access_token_invalid(auth: Auth):
    with pytest.raises(AuthException) as e:
        auth.refresh_access_token("invalid_refresh_token")
    assert str(e.value) == "Invalid token"


def test_refresh_access_token_expired(auth: Auth, mocker: MockerFixture):
    # I failed to reproduce token expiration error so let's mock it
    mocker.patch("python_utils.auth.decode", side_effect=ExpiredSignatureError)
    refresh_token = auth.create_refresh_token({"username": "username"})
    with pytest.raises(AuthException) as e:
        auth.refresh_access_token(refresh_token)
    assert str(e.value) == "Token expired"


def test_refresh_access_token_invalid_refresh_token(auth: Auth):
    with pytest.raises(AuthException) as e:
        auth.refresh_access_token("invalid_refresh_token")
    assert str(e.value) == "Invalid token"


@pytest.mark.asyncio
async def test_get_current_user(auth: Auth):
    token = auth.create_access_token({"username": "username"})
    username = await auth.get_current_user(token)
    assert username == "username"
