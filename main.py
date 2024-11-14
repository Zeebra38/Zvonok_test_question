import re

from collections import defaultdict


class TimeKeeper:
    """
    Получает логи из хранилища, в котором они лежат в формате
    Андрей 9
    Василий 11
    Роман 7
    X Æ A-12 45
    Иван Петров 3
    ..
    Андрей 6

    А затем рассчитывает суммарное время, отработанное каждом сотрудником, в формате
    Андрей: 9, 6; sum: 15
    Василий: 11; sum: 11
    Роман: 7, 11; sum: 18
    """

    log_row_pattern = re.compile(r"^(.*)\s+(\d+)$")  # Одна строка выглядит как "Иван Петров 3"

    def __init__(self, filename: str | None = None):
        self.filename = filename or "logs.txt"

    def handle(self) -> None:
        log_content = self.get_log_content_from_file(self.filename)

        hours_by_worker = defaultdict(list)
        for row in log_content.split("\n"):
            row = row.strip()

            match = self.log_row_pattern.search(row)
            if not match:  # Случай, когда строка является разделителем дней
                continue

            worker, hours = match.group(1), match.group(2)

            hours_by_worker[worker.strip()].append(int(hours))

        for worker, hours in hours_by_worker.items():
            hours_str = ", ".join(map(str, hours))
            print(f"{worker}: {hours_str}; sum: {sum(hours)}")

    @staticmethod
    def get_log_content_from_file(filename: str) -> str:
        """Получает пользовательский ввод. Так как в задаче не указано как именно, то будет использовать файл"""
        with open(filename, 'rb') as f:
            log_content = f.read()
        return log_content.decode()


time_keeper = TimeKeeper()
time_keeper.handle()
