from unittest import TestCase
from unittest.mock import patch, call, MagicMock

from main import TimeKeeper


class TestTimeKeeper(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.time_keeper = TimeKeeper()

    @patch("builtins.print")
    def test_ok(self, print_mock: MagicMock):
        log_content = """
        Андрей 1
        Иван1 2 4
        ИВАн 3
        иван            10
        Андрей 5
        İnanç Esasları 2
        İnanç Esasları 3
        """

        with patch(
            "main.TimeKeeper.get_log_content_from_file", return_value=log_content
        ):
            self.time_keeper.handle()

        print_mock.assert_has_calls(
            [
                call("Андрей: 1, 5; sum: 6"),
                call("Иван1 2: 4; sum: 4"),
                call("ИВАн: 3; sum: 3"),
                call("иван: 10; sum: 10"),
                call("İnanç Esasları: 2, 3; sum: 5"),
            ]
        )

    @patch("builtins.print")
    def test_empty_log(self, print_mock: MagicMock):
        log_content = ""

        with patch(
            "main.TimeKeeper.get_log_content_from_file", return_value=log_content
        ):
            self.time_keeper.handle()

        print_mock.assert_not_called()
