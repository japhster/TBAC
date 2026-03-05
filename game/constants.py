from django.db import models

MOVE_COMMAND = "MOVE"
TAKE_COMMAND = "TAKE"
OPEN_COMMAND = "OPEN"
USE_COMMAND = "USE"
INSPECT_COMMAND = "INSPECT"

COMMAND_OPTIONS = {
    MOVE_COMMAND: [MOVE_COMMAND, "GO", "EXPLORE", "ENTER", "LEAVE"],
    TAKE_COMMAND: [TAKE_COMMAND],
    OPEN_COMMAND: [OPEN_COMMAND],
    USE_COMMAND: [USE_COMMAND],
    INSPECT_COMMAND: [INSPECT_COMMAND, "LOOK", "DESCRIBE"],
}

ALL_COMMANDS = sum(COMMAND_OPTIONS.values(), start=[])


FAILED_TO_INTERPRET_COMMAND_MESSAGE = (
    "You attempted to do something"
    " but aren't really sure what it was you wanted to achieve."
)
