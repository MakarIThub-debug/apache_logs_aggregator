import re
import sqlite3

class LogEntry:
    def __init__(self, h: str = None, l: str = None, u: str = None, t: str = None, r: str = None, s: str = None, b: str = None):
        self.h = h
        self.l = l
        self.u = u
        self.t = t
        self.r = r
        self.s = s
        self.b = b

    def __repr__(self):
        return f'{self.h}, {self.l}, {self.u}, {self.t}, {self.r}, {self.s}, {self.b}'


def read_config(filename):
    with open(filename, 'r', encoding='UTF-8') as f:
        lines = f.readlines()
    directory = re.findall(r'"(.*)"', lines[0])[0].replace('\\', '/')
    return directory


def read_logs(directory):
    with open(directory, 'r', encoding='UTF-8') as f:
        lines = f.readlines()
    lines = [line.rstrip() for line in lines]
    pattern = r'(^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) (.*) (.*) \[(\d{2}\/\w*\/\d{4}:\d{2}:\d{2}:\d{2} [+,-]\d{4})\] "(.*)" (\d*) (\d*)'
    return [LogEntry(*re.split(pattern, line)[1:-1]) for line in lines if re.match(pattern, line)]


def write_to_db(data):
    with sqlite3.connect('Parser.db') as con:
        cursor = con.cursor()
        try:
            for log in data:
                cursor.execute("""INSERT OR IGNORE INTO logs
                                  (h, l, u, t, r, s, b)
                                  VALUES (?, ?, ?, ?, ?, ?, ?);""", (log.h, log.l, log.u, log.t, log.r, log.s, log.b))
            con.commit()
            print(f"Запись успешно дабавленна в таблицу. Количество строк: {cursor.rowcount}")
        except sqlite3.Error as error:
            print(f"Ошибка при работе с SQLite: {error}")


def select_to_user():
    with sqlite3.connect('Parser.db') as con:
        cursor = con.cursor()
        try:
            print('h - IP address, l - Lengthy hostname of remote host, u - Remote user, t - Time of request, r - First request line, s - Final status, b - Size of response in bytes')
            query = input('Перечислите параметры, которые нужно вывести: ')
            if input('Вам нужен временной диапазон в вашем запросе?: ') == 'Да':
                start_time = input('Введите начальную точку времени (ЧЧ:MM:СС): ')
                end_time = input('Введите конечнуею точку времени (ЧЧ:MM:СС): ')
                start_time_int = int(start_time.replace(':', ''))
                end_time_int = int(end_time.replace(':', ''))
                query_time = f"CAST((substr(t, 13, 2)||substr(t, 16, 2)||substr(t, 19, 2)) AS INTEGER)"
                ans = cursor.execute(f"""SELECT {query} FROM logs WHERE {query_time} BETWEEN ? AND ?;""", (start_time_int, end_time_int)).fetchall()
            else:
                ans = cursor.execute(f"""SELECT {query} FROM logs;""").fetchall()
            print(ans)
        except sqlite3.Error as error:
            print(f"Возникла ошибка при взаимодействии с SQLite: {error}!!! ")


dir = read_config('cfg.txt')
logs_arr = read_logs(dir)
write_to_db(logs_arr)
select_to_user()