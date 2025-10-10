import pytest

from app.domain.hasher.hasher import PasswordHasher


class TestHasher:

    def test_verify_password_correct(self):
        password = "mysecretpassword"
        hashed_password = PasswordHasher.hash_password(password)

        assert PasswordHasher.verify_password(password, hashed_password) is True
        assert hashed_password != password

    def test_verify_password_incorrect(self):
        correct_password = "mysecretpassword"
        wrong_password = "anotherpassword"
        hashed_password = PasswordHasher.hash_password(correct_password)

        assert PasswordHasher.verify_password(wrong_password, hashed_password) is False

    def test_hash_properties_meet_nfr(self):
        password = "a_password_for_nfr_check"
        hashed_password = PasswordHasher.hash_password(password)

        assert hashed_password.startswith("$2b$")

        try:
            parts = hashed_password.split("$")
            cost_factor = int(parts[2])

            assert cost_factor == 12
        except (IndexError, ValueError) as e:
            pytest.fail(f"Could not parse bcrypt hash to verify cost factor: {e}")

    @pytest.mark.parametrize(
        "password",
        [
            "shrt_password",
            "a_long_password_over_72_chars_adadnadnmasndmasndmansdmna,dsna,snd,ands,",
            "password_with_unicode_&_symbols_!@#$%",
            "",
        ],
    )
    def test_hashing_with_various_passwords(self, password: str):
        hashed = PasswordHasher.hash_password(password)
        assert PasswordHasher.verify_password(password, hashed) is True
