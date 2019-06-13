import click
import os

from app import create_app
from app.modules.users import UserRoles, save_new_user

__author__ = 'Tharun M Paul (tmpaul06@gmail.com)'

# https://stackoverflow.com/questions/41268949/python-click-option-with-a-prompt-and-default-hidden
class HiddenPassword(object):
    def __init__(self, password=''):
        self.password = password

    def __str__(self):
        return self.password[:2] + (len(self.password) - 2) * '*' + \
               self.password[-2:]


@click.command()
@click.option('--email', help='Superuser email')
@click.option('--password', prompt=True, hide_input=True)
@click.option('--first-name', help='First name')
@click.option('--last-name', help='Last name')
def create_user(email, password, first_name, last_name):
    """Create a superuser in the system with provided parameters"""
    print(email, HiddenPassword(password), first_name, last_name)
    input('\n Confirm you want to proceed ? Press Ctrl-C or Cmd-C to abort')
    with create_app(os.getenv('FLASK_CONFIG', 'development')).app_context():
        save_new_user({
            'email': email,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'role': UserRoles.SYS_ADMIN
        })

if __name__ == '__main__':
    create_user()
