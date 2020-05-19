import fbchat
from getpass import getpass
import re


class FB_Notifier:
    """interface for sending messages through fbchat library"""
    def __init__(self, username: str, password: str, recipient: str):
        self._username = username
        self._password = password
        self._recipient = recipient
        self._client = fbchat.Client(username, password)


    def __call__(self, message: str) -> str:
        """sends the given message"""
        self._client.send(fbchat.models.Message(text=message),
            thread_id=self._recipient,
            thread_type=fbchat.models.ThreadType.USER)
        return f'''The message "{message}" was sent to {self._recipient}'''

    def logout(self):
        """logs out of Facebook account"""
        return self._client.logout()


def connect() -> FB_Notifier:
    """construts messenger interface, logged in from inputted credentials"""
    username = _input_username()
    password = _input_password()
    recipient = input('Message recipient: ')
    return FB_Notifier(username, password, recipient)


def _input_username() -> str:
    while True:
        username = input('Please specify a username: ')
        if re.match("^[^\s]+$", username):
            return username
        print('Not a valid username. Try again.')


def _input_password() -> str:
    while True:
        password = getpass('Please specfiy a password: ')
        if len(password) > 0:
            return password
        print('The password cannot be empty. Try Again')
