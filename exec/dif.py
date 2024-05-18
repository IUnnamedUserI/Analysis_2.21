from datetime import datetime
import argparse
import psycopg2
from psycopg2 import sql


def print_help():
    """
    Функция вывода доступных пользователю команд
    """
    print("list - вывод всех добавленных записей")
    print("add - добавление новых записей")
    print("find - найти запись по фамилии")
    print("exit - завершение работы программы")


def add_worker(cursor, surname, name, phone, date):
    """
    Функция добавления новой записи
    """
    cursor.execute(
        sql.SQL("INSERT INTO workers (surname, name, phone, date) VALUES (%s, %s, %s, %s)"),
        (surname, name, phone, date)
    )
    print("Запись успешно добавлена")


def print_list(cursor):
    """
    Функция выводит на экран список всех существующих записей
    """
    cursor.execute("SELECT surname, name, phone, date FROM workers")
    for row in cursor.fetchall():
        print(f"{row[0]} {row[1]} | {row[2]} | {row[3]}")


def find_member(cursor, period):
    """
    Функция для вывода на экран всех записей, чьи фамилии совпадают
    с введённой и чей год поступления на работу не ранее указанного
    """
    cursor.execute(
        sql.SQL("SELECT surname, name, phone, date FROM workers WHERE extract(year from date) <= %s"),
        (datetime.now().year - period,)
    )
    return cursor.fetchall()


def main():
    parser = argparse.ArgumentParser("workers")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )

    parser.add_argument(
        "--host",
        action="store",
        default="localhost",
        help="PostgreSQL server host"
    )
    parser.add_argument(
        "--port",
        action="store",
        default="5432",
        help="PostgreSQL server port"
    )
    parser.add_argument(
        "--database",
        action="store",
        default="workersDB",
        required=False,
        help="PostgreSQL database name"
    )
    parser.add_argument(
        "--user",
        action="store",
        required=False,
        help="PostgreSQL user"
    )
    parser.add_argument(
        "--password",
        action="store",
        required=False,
        help="PostgreSQL password"
    )

    subparsers = parser.add_subparsers(dest="command")

    add = subparsers.add_parser("add", help="Add a new worker")
    add.add_argument("-s", "--surname", action="store", required=True, help="The worker's surname")
    add.add_argument("-n", "--name", action="store", required=True, help="The worker's name")
    add.add_argument("-p", "--phone", action="store", help="The worker's phone")
    add.add_argument("-d", "--date", action="store", required=True, help="The date of hiring")

    _ = subparsers.add_parser("display", help="Display all workers")

    select = subparsers.add_parser("select", help="Select the workers")
    select.add_argument("-p", "--period", action="store", type=int, required=True, help="The required period")

    args = parser.parse_args()

    conn = psycopg2.connect(
        host=args.host,
        port=args.port,
        database=args.database,
        user="postgres",
        password="admin"
    )

    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS workers (surname VARCHAR, name VARCHAR, phone VARCHAR, date DATE)")

    if args.command == "add":
        add_worker(cursor, args.surname, args.name, args.phone, args.date)
        conn.commit()

    elif args.command == "display":
        print_list(cursor)

    elif args.command == "select":
        selected = find_member(cursor, args.period)
        for row in selected:
            print(f"{row[0]} {row[1]} | {row[2]} | {row[2]}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
