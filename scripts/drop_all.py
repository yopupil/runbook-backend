"""
Script to drop all tables from DB for a fresh start.

Warning!!! Do not use against live database for whatsoever reason
unless you know what you are doing
"""
# encoding: utf-8
import os
import sys
from app import create_app
from app.extensions import db

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


if __name__ == '__main__':
    t = input('Confirm that you want to drop the database ? If yes, type name of db: ')
    a = create_app(os.getenv('FLASK_ENVIRONMENT_TYPE', 'testing'))
    if t != a.config['DB_NAME']:
        print('Incorrect DB name, Exiting!')
        sys.exit(0)

    input('\nYou are about to drop db tables. Sure ?')
    input('Did you think it is that easy ??? Are you doubly sure ??')
    input('Okay one last time baby! You sure about this ?')
    input('Your funeral. Press any key')

    with a.app_context():
        db.init_app(a)

        db.drop_all()

        db.engine.execute('DROP TABLE IF EXISTS alembic_version;')
