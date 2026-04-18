#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

    try:
        import pymysql
        pymysql.install_as_MySQLdb()
    except ImportError:
        raise ImportError(
            "PyMySQL is required to use the MySQL backend with this project. "
            "Install it with `pip install PyMySQL` or add it to requirements.txt."
        )

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
