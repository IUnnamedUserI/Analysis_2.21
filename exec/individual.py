#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Для своего варианта лабораторной работы 2.17 необходимо реализовать
хранение данных в базе данных SQLite3. Информация в базе данных
должна храниться не менее чем в двух таблицах.
"""

import argparse
from pathlib import Path
import sqlite3
import typing as t


def print_help():
    """
    Функция вывода доступных пользователю команд
    """

    print("list - вывод всех добавленных записей")
    print("add - добавление новых записей")
    print("find - найти запись по фамилии")
    print("exit - завершение работы программы")


def add_worker(database_path: Path, name: str, phone: str, year: int) -> None:
    """
    Функция добавления новой записи, возвращает запись
    """
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO workers (worker_name, phone_number, worker_year)
        VALUES (?, ?, ?)
        """,
        (name, phone, year)
    )

    connection.commit()
    connection.close()


def print_list(staff: t.List[t.Dict[str, t.Any]]) -> None:
    """
    Функция выводит на экран список всех существующих записей
    """
    if staff:
        line = '+-{}-+-{}-+-{}-+-{}-+'.format(
            '-' * 4,
            '-' * 30,
            '-' * 20,
            '-' * 8
        )
        print(line)

        print(
            '| {:^4} | {:^30} | {:^20} | {:^8} |'.format(
                "№",
                "Ф.И.О.",
                "Номер телефона",
                "Год"
            )
        )
        print(line)

        for idx, worker in enumerate(staff, 1):
            print(
                '| {:>4} | {:<30} | {:<20} | {:>8} |'.format(
                    idx,
                    worker.get('name', ''),
                    worker.get('phone_number', ''),
                    worker.get('year', 0)
                )
            )
            print(line)

    else:
        print("Список работников пуст.")


def create_db(database_path: Path) -> None:
    """
    Создание базы данных
    """
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS workers (
            worker_id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            worker_year INTEGER NOT NULL
        )
        """
    )

    connection.close()


def select_all(database_path: Path) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбор всех записей из базы данных
    """
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT workers.worker_name, workers.phone_number, workers.worker_year
        FROM workers
        """
    )
    rows = cursor.fetchall()

    connection.close()
    return [
        {
            "name": row[0],
            "phone_number": row[1],
            "year": row[2],
        }
        for row in rows
    ]


def select_by_period(
    database_path: Path, period: int
) -> t.List[t.Dict[str, t.Any]]:
    """
    Выборка по периоду
    """
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT workers.worker_name, workers.phone_number, workers.worker_year
        FROM workers
        WHERE (strftime('%Y', date('now')) - workers.worker_year) >= ?
        """,
        (period,)
    )
    rows = cursor.fetchall()

    connection.close()
    return [
        {
            "name": row[0],
            "phone_number": row[1],
            "year": row[2],
        }
        for row in rows
    ]


def main(command_line=None):
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "--db",
        action="store",
        required=False,
        default=str(Path.home() / "workers.db"),
        help="Название файла базы даанных"
    )

    parser = argparse.ArgumentParser("workers")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )

    subparsers = parser.add_subparsers(dest="command")

    add = subparsers.add_parser(
        "add",
        parents=[file_parser],
        help="Add a new worker"
    )
    add.add_argument(
        "-n",
        "--name",
        action="store",
        required=True,
        help="Имя работника"
    )
    add.add_argument(
        "-p",
        "--phone",
        action="store",
        help="Номер телефона работника"
    )
    add.add_argument(
        "-y",
        "--year",
        action="store",
        required=True,
        help="Дата нанятия"
    )

    _ = subparsers.add_parser(
        "display",
        parents=[file_parser],
        help="Вывести на экран всех работников"
    )

    select = subparsers.add_parser(
        "select",
        parents=[file_parser],
        help="Выборка работников"
    )
    select.add_argument(
        "-p",
        "--period",
        action="store",
        type=int,
        required=True,
        help="Требуемый период"
    )

    args = parser.parse_args(command_line)

    db_path = Path(args.db)
    create_db(db_path)

    if args.command == "add":
        add_worker(db_path, args.name, args.phone, args.year)

    elif args.command == "display":
        print_list(select_all(db_path))

    elif args.command == "select":
        print_list(select_by_period(db_path, args.period))
        pass


if __name__ == "__main__":
    """
    Основная программа
    """
    main()
