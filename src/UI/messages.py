from builtins import str
from dataclasses import dataclass
import textwrap

from utils.initialize_all import initialize_all_pre


@dataclass
class Message:
    text : str
    color : namedtuple('color', 'R G B') = (255, 255, 255)


class MessageLog:

    @initialize_all_pre
    def __init__(self, x, width, height):
        self.messages = []

    def add_message(self, message):
        # Split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(message.text, self.width)

        for line in new_msg_lines:
            # If the buffer is full, remove the first line to make room for the new one
            if len(self.messages) == self.height:
                del self.messages[0]

            # Add the new line as a Message object, with the text and the color
            self.messages.append(Message(line, message.color))
