import unittest
import json
from bot import opt_in, opt_out, user_in_opt_board, load_file, save_file


class DatabaseTest(unittest.TestCase):

    def test_board_check(self):
        filename = "../resources/optin-db.json"
        self.assertTrue(
            user_in_opt_board(
                "test", filename=filename),
                "Board checker failed to observe a present name in board -> user_in_opt_board")
        self.assertFalse(
            user_in_opt_board(
                "failed_test", filename=filename),
                "Board checker observed an absent name in board -> user_in_opt_board")

    def test_add_user(self):
        filename = "../resources/optin-db.json"
        user = "test_user_id"
        opt_in(user, filename=filename)

        self.assertTrue(user_in_opt_board(user, filename=filename), "Failed to add user to database -> opt_in")

    def test_remove_user(self):
        filename = "../resources/optin-db.json"
        user = "test_user_id"
        opt_out(user, filename=filename)

        self.assertFalse(user_in_opt_board(user, filename=filename), "Failed to remove user to database -> opt_out")

