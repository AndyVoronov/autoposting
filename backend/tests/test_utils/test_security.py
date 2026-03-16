import pytest
from datetime import datetime, timedelta
from unittest.mock import patch


class TestVerifyPassword:
    def test_verify_password_correct(self):
        from app.utils.security import verify_password, get_password_hash

        password = "test_password_123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        from app.utils.security import verify_password, get_password_hash

        password = "test_password_123"
        hashed = get_password_hash(password)

        assert verify_password("wrong_password", hashed) is False

    def test_verify_password_empty(self):
        from app.utils.security import verify_password, get_password_hash

        hashed = get_password_hash("password")

        assert verify_password("", hashed) is False


class TestGetPasswordHash:
    def test_get_password_hash_creates_hash(self):
        from app.utils.security import get_password_hash

        password = "test_password_123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 20

    def test_get_password_hash_different_for_same_password(self):
        from app.utils.security import get_password_hash

        password = "test_password_123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2


class TestCreateToken:
    def test_create_token_success(self):
        from app.utils.security import create_token

        token = create_token({"sub": "123", "user_id": 1})

        assert token is not None
        assert len(token) > 20

    def test_create_token_with_expiration(self):
        from app.utils.security import create_token

        expires = timedelta(hours=1)
        token = create_token({"sub": "123"}, expires_delta=expires)

        assert token is not None

    def test_create_token_default_expiration(self):
        from app.utils.security import create_token, create_token as original_create

        with patch("app.utils.security.settings") as mock_settings:
            mock_settings.JWT_EXPIRE_MINUTES = 60
            mock_settings.SECRET_KEY = "test-secret-key-for-testing"
            mock_settings.JWT_ALGORITHM = "HS256"

            token = create_token({"sub": "123"})
            assert token is not None


class TestDecodeToken:
    def test_decode_token_success(self):
        from app.utils.security import create_token, decode_token

        with patch("app.utils.security.settings") as mock_settings:
            mock_settings.SECRET_KEY = "test-secret-key-for-testing"
            mock_settings.JWT_ALGORITHM = "HS256"

            token = create_token({"sub": "123", "user_id": 1})
            decoded = decode_token(token)

            assert decoded is not None
            assert decoded["sub"] == "123"
            assert decoded["user_id"] == 1

    def test_decode_token_invalid(self):
        from app.utils.security import decode_token

        decoded = decode_token("invalid_token")

        assert decoded is None

    def test_decode_token_expired(self):
        from app.utils.security import create_token, decode_token

        with patch("app.utils.security.settings") as mock_settings:
            mock_settings.SECRET_KEY = "test-secret-key-for-testing"
            mock_settings.JWT_ALGORITHM = "HS256"

            past_time = datetime.utcnow() - timedelta(hours=2)
            with patch("app.utils.security.datetime") as mock_datetime:
                mock_datetime.utcnow.return_value = past_time

                token = create_token({"sub": "123"})

            current_time = datetime.utcnow()
            with patch("app.utils.security.datetime") as mock_datetime:
                mock_datetime.utcnow.return_value = current_time

                decoded = decode_token(token)
                assert decoded is None

    def test_decode_token_wrong_secret(self):
        from app.utils.security import create_token, decode_token

        with patch("app.utils.security.settings") as mock_settings:
            mock_settings.SECRET_KEY = "test-secret-key-for-testing"
            mock_settings.JWT_ALGORITHM = "HS256"

            token = create_token({"sub": "123"})

            with patch("app.utils.security.settings.JWT_ALGORITHM") as mock_algo:
                mock_algo.SECRET_KEY = "wrong-secret-key"

                decoded = decode_token(token)
                assert decoded is None
