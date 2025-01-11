from enum import StrEnum


class CWCommandType(StrEnum):
    FIRST = 'first'
    MOVE = 'move'
    MSG = 'msg'
    ACTION = 'action'
    FIGHT_BLOCK = 'fight block'
    FIGHT_ATTACK = 'fight attack'
    START_ROTATE = 'fight rotate'
    STOP_ROTATE = 'fight stopRotate'


class CWActionType(int):
    # Solo actions
    CANCEL = 0
    "Cancel current action"
    SLEEP = 1
    LICK_SELF = 3
    SMELL_SELF = 13
    DIG = 17
    ENTER_COMBAT = 27
    EXIT_COMBAT = 28

    # Actions with other players (require ID)
    PICK = 6
    SMELL_CAT = 14
    LICK_CAT = 19
    CHEEK_CAT = 51
