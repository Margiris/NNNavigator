import os
from enum import Enum


class Color(Enum):
    def RED(): return (255, 0, 0)
    def GREEN(): return (0, 255, 0)
    def BLUE(): return (0, 0, 255)
    def BLACK(): return (0, 0, 0)
    def WHITE(): return (255, 255, 255)


def confirmationDialog(message):
    return
