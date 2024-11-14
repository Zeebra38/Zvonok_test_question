# Мое решение тестового задания

## 1. Задача на подумать
```
Есть веб-сервис А, принимающий запросы от пользователей, запросов может приходить в час 200 000. В день приходит до 2 000 000 запросов
Сервис А должен отправить эти данные в сервис Б, чтоб обработать данные. 
Сервис Б может обработать 100 000 запросов в час. 
Запросы от пользователей поступающий в сервис А нельзя потерять.
Как бы вы организовали межсервисное взаимодействие, хранение данных, результатов, какие инструменты  использовали бы для этого?
```

### Ответ

Есть **несколько** вариантов решения данной задачи. Я опишу в основном подход через очередь сообщений, но можно сделать также через таблицу в NoSQL базе, например ClickHouse, со своими плюсами и минусами. В нее можно батчами записывать данные, и оттуда же их доставать и редактировать в сервисе Б.  

Так как сервис Б не может справиться с нагрузкой от сервиса А за час (но может за сутки), то тут есть вариант **масштабировать** количество сервисов Б (можно сделать автоматизированно через K8S, например), если нам нужно снизить общее время реакции
на событие от пользователя, или можно подождать и тогда за сутки сервис Б должен успеть обработать всю очередь. *Стоит добавить мониторинги и алерты на количество необработанных сообщений в очереди, чтобы иметь возможность следить за ситуацией и
если сервис Б не будет успевать обработать все события за день, то масштабировать его*  

#### Очередь
В качестве очереди можно использовать несколько вариантов. Если сообщения небольшие по содержимому, то можно использовать RabbitMQ, Celery или другие брокеры сообщений. Потенциально универсальным решением будет Kafka, но она более требовательна к ресурсам, зато и обладает большими
возможностями. Если в компании уже есть Kafka, то можно писать в нее в отдельный топик. Однако я бы остановился на вариантс с RabbitMQ в общем случае, а дальше нужно смотреть конкретнее на ситуацию.

#### Хранение результатов
Это зависит от того, что нам вообще нужно получить в результате. Это может запись в логах о том, что запрос обработан и передан во внешнее API, например, в таком случае подойдет NoSQL БД. Если же нам нужно обработать/создать записи в нашей реляционной БД,
то это может быть **И** запись в таблице логах о полученном запросе, его обработке, **И** изменений в записях реляционной БД.  
Стоит логировать все запросы от пользователя и все этапы обработки (получение их сервисом Б, успешная обработка, ошибки в процессе). Если не хочется хранить всю историю, то можно дропать старые записи в логах после полугода, например.  
Но допустим, размер сообщения в utf8 по 200 символов это будет 200 байт. В день 400 млн = 380 мб. 

#### Мониторинг
Очень важно мониторить процесс, если нам нельзя потерять события. Для этого можно использовать Prometeus для метрик, логи из приложения, дашборды в Grafana.  
Самое простое - сделать регулярные SQL-запросы по таблице с логами, которые будут мониторить процент успешных обработок. Если он меньше 99%, то кидать алерт.  
Дальше можно настроить дашборды в Grafana с возможностью on-call звонков.  
Мониторить нужно количество предметов в очереди, сроки выполнения каждой задачи, время ответа API сервиса A, этапы обработки задачи в сервисе Б, все ошибки в обоих сервисах. Так как нагрузка высокая и время простоя нужно минимально снизить, то графики  
позволять увидеть потенциальные проблемы до того, как они дойдут до пользователей


#### Еще один вариант
Так как сервис Б не справляется с пиковой нагрузкой от сервиса А, то можно подумать над созданием сервиса В, который будет обрабатывать тяжелую часть запросов, разгрузив сервис Б. Если такой вариант возможен, то он может быть даже лучше, чем масштабировать сервис Б.  
Но нужно смотреть на конкретные случаи.


## 2. Ссылка на задание  https://gitlab.zvonok.in/-/snippets/28 

### 2.1 SQL
```
Даны две таблицы в PostgresSQL - таблица статей и таблица комментариев к этим статьям.
Необходимо написать запрос, который выведет все статьи без комментариев (у которых нет комментариев)
Таблицы тут: http://sqlfiddle.com/#!17/84c62 (Или тут https://www.db-fiddle.com/f/kGzmoWLCRkQ9mzHM83u2vT/0)
(Проверочный результат - статьи с id 2 и 3)
```

```sql
CREATE TABLE article (
    id        integer CONSTRAINT articlekey PRIMARY KEY,
    title       varchar(255) NOT NULL,
    text         text NOT NULL
);


CREATE TABLE comment (
    id        integer CONSTRAINT commentkey PRIMARY KEY,
    article_id integer NOT NULL,
    text         text NOT NULL
);


INSERT INTO article (id, title, text) VALUES (1, 'Phasellus gravida eu ante et imperdiet', 'Mauris rutrum augue risus, sodales maximus neque vulputate a. Curabitur porttitor, risus eu fermentum hendrerit, urna est dictum est, quis condimentum lectus nisi eget diam.');
INSERT INTO article (id, title, text) VALUES (2, 'Maecenas egestas fermentum rutrum', 'Vivamus varius nibh et iaculis mollis. Phasellus eu massa a libero eleifend scelerisque. Nulla molestie justo libero, ac aliquet mi iaculis eget.');
INSERT INTO article (id, title, text) VALUES (3, 'Nam vestibulum dignissim volutpat', 'Praesent neque lectus, porttitor et nunc vitae, congue semper felis. Pellentesque convallis facilisis odio id fringilla. Vivamus quis nibh felis.');
INSERT INTO article (id, title, text) VALUES (4, 'Phasellus augue ipsum, rutrum a imperdiet', 'Praesent in turpis ac nisl pellentesque volutpat. Maecenas vitae viverra ipsum. Proin accumsan diam vitae nulla tincidunt, a mollis diam luctus.');
INSERT INTO article (id, title, text) VALUES (5, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit', 'Integer eget urna porttitor, dictum quam quis, cursus tellus. Pellentesque dictum accumsan mauris a pulvinar.');

INSERT INTO comment (id, article_id, text) VALUES (1, 1, 'Nunc ac arcu non lectus bibendum mattis. Suspendisse suscipit, enim sit amet ultrices laoreet, dolor dui rhoncus quam');
INSERT INTO comment (id, article_id, text) VALUES (2, 1, 'Aenean cursus a sapien ac malesuada');
INSERT INTO comment (id, article_id, text) VALUES (3, 1, 'Fusce sit amet lacus dignissim, tempus massa sed, ultricies dolor');
INSERT INTO comment (id, article_id, text) VALUES (4, 4, 'Phasellus non urna commodo, finibus lectus ac, gravida lectus');
INSERT INTO comment (id, article_id, text) VALUES (5, 4, 'Suspendisse pretium porttitor iaculis. Nulla in tortor vel est lobortis fermentum');
INSERT INTO comment (id, article_id, text) VALUES (6, 4, 'Etiam gravida vehicula massa non condimentum');
INSERT INTO comment (id, article_id, text) VALUES (7, 4, 'Etiam rutrum purus a ipsum viverra laoreet. Nunc aliquet ex vitae tincidunt luctus');
INSERT INTO comment (id, article_id, text) VALUES (8, 4, 'Sed facilisis fermentum lacus, non semper est sodales sed.');
INSERT INTO comment (id, article_id, text) VALUES (9, 5, 'Integer vitae ipsum auctor, interdum leo eu, facilisis dui. Suspendisse ut feugiat dolor, in ultrices leo');
```

### Ответ:
Оптимальным способом будет использование LEFT OUTER JOIN, так как нам не придется считывать всю таблицу в память, как при использовани подзапроса.
```
SELECT a.id as "article_id"
FROM article a
LEFT OUTER JOIN comment c ON c.article_id = a.id
WHERE c.id IS NULL;
```
Мы получим все записи, для которых не получилось найти комментарии. LEFT OUTER JOIN именно это и делает, так как он плучает комментарии даже для тех статей, для которых они не заданы. В таком случае все значения будут равны NULL у таблицы `comment`

#### Дополнение к ответу
Стоит в таблицу comment добавить индекс по `article_id`, так как это сильно ускорит SELECT на больших объемах данных в будущем. И **потенциально** стоит добавить Foreign Key на `article_id`, однако это имеет свои плюсы и минусы. Плюсом является контроль целостности со стороны БД, а минусом потенциаьно более долгие INSERT/UPDATE, что для миллионов комментариев может быть критично. Можно поддерживать целостность со стороны моделей, например в Django.
```
CREATE INDEX idx_comment_article_id ON comment(article_id);

ALTER TABLE comment
    ADD CONSTRAINT fk_comment_article_id FOREIGN KEY (article_id) REFERENCES article (id);
```
В данном примере это не повлияет на время выполнения, как мы можем увидеть в `EXPLAIN ANALYSE`, но в будущем таблица комментариев 

### 2.2 Программа учета времени
```
На входе есть такие записи выполненных часов работниками
(по дням, дни можно опустить - они не имеют значения):
Формат - имя, пробел, число.
Если имя повторяется, то это один и тот же работник. Имя может содержать пробелы и цифры.
```
```
Андрей 9
Василий 11
Роман 7
X Æ A-12 45
Иван Петров 3
..
Андрей 6
Роман 11
...
```

```
Необходимо написать программу на python, которая выводит статистику по каждому работнику + сумму часов, например:
```

```
Андрей: 9, 6; sum: 15
Василий: 11; sum: 11
Роман: 7, 11: sum: 18
...
```

### Ответ:
Более подробно ответ представлен в прикрепленных файлах. В файле `main.py` представлено решение в виде класса 
`TimeKeeper` и его запуск с чтением из файла логов `logs.txt`. В файле `test_timekeeper.py` представлены unit-тесты.  

```py
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
```
