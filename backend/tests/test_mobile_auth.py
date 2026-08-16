from __future__ import annotations

import unittest

from backend.mobile_auth import MIN_TOKEN_LENGTH, bearer_is_valid, validate_mobile_token


class MobileAuthTests(unittest.TestCase):
    def test_rejects_missing_and_short_tokens(self) -> None:
        for value in (None, "", "short", " " * MIN_TOKEN_LENGTH):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_mobile_token(value)

    def test_accepts_strong_token_without_changing_it(self) -> None:
        token = "a" * MIN_TOKEN_LENGTH
        self.assertEqual(validate_mobile_token(token), token)

    def test_bearer_header_must_match_exactly(self) -> None:
        token = "a" * MIN_TOKEN_LENGTH
        self.assertTrue(bearer_is_valid(f"Bearer {token}", token))
        self.assertFalse(bearer_is_valid(None, token))
        self.assertFalse(bearer_is_valid(token, token))
        self.assertFalse(bearer_is_valid(f"bearer {token}", token))
        self.assertFalse(bearer_is_valid("Bearer wrong", token))


if __name__ == "__main__":
    unittest.main()
