import textwrap
import typing

import utilities.constants


class Message:
    def __init__(self, text, color: typing.Tuple[int, int, int] = utilities.constants.WHITE):
        self.text = text
        self.color = color


class MessageLog:
    def __init__(self, width, height):
        self.messages = []
        # self.x = x
        self.width = width
        self.height = height

    def add_message(self, message):
        # Split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(message.text, self.width)

        if new_msg_lines is not None:
            new_msg_lines.reverse()

        for line in new_msg_lines:
            # If the buffer is full, remove the first line to make room for the new one
            if len(self.messages) == self.height:
                del self.messages[0]

            # Add the new line as a Message object, with the text and the color
            self.messages.append(Message(line, message.color))

global message_log

message_log = MessageLog(utilities.constants.MESSAGE_LOG_WIDTH // utilities.constants.FONT_SIZE,
                                                         utilities.constants.MAX_MESSAGES)