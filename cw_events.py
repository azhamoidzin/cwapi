from abc import ABC
from enum import StrEnum
from utils.date_utils import millis_to_str
from junk.clan_enum import ClanEnum
import json


class CWEventType(StrEnum):
    NO_EVENT = ''
    DATA = 'data'
    UPDATE = 'update'
    UPDATE_CAT = 'update cat'
    MOVE = 'move'
    LEAVE_LOCATION = 'LEAVE LOCATION'
    UPDATE_ACTION = 'update ACTION'
    MESSAGE = 'msg'
    MESSAGES_LOAD = 'msg load'
    FIELD = 'field'
    LOCATION = 'location'


class CWEvent(ABC):
    def __init__(self, event_type: CWEventType, event_str: str = '', raw_event_dict: dict | None = None):
        self.event_type = event_type
        self.event_str = event_str
        self.raw_event_dict = raw_event_dict

    def __str__(self):
        return self.event_str

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def from_raw_message(raw_message: str):
        data = None
        try:
            data = raw_message[2:]
            items = json.loads(data)
            if len(items) != 2:
                return CWEvent(CWEventType.NO_EVENT)
            action_type, data = items
            match action_type:
                case CWEventType.MESSAGE:
                    return MessageEvent(
                        data['id'],
                        data['text'],
                        data['cat'],
                        data['time'],
                        data['volume'],
                        data['login'],
                        data['textTransformation'],
                    )
                case CWEventType.MESSAGES_LOAD:
                    unique_messages = {msg['id']: msg for msg in data}.values()
                    return MessageLoadEvent([MessageEvent(
                        message['id'],
                        message['text'],
                        message['cat'],
                        message['time'],
                        message['volume'],
                        message['login'],
                        message['textTransformation'],
                    ) for message in unique_messages])
                case CWEventType.FIELD:
                    return FieldEvent(
                        data['huntMode'],
                        data['music'],
                        data['wer'],
                        data['rotate'],
                        data['users'],
                        data['map'],
                        data['items'],
                        data['catsTaken'],
                        data['itemsTaken'],
                        data['puddles'],
                    )
                case CWEventType.DATA:
                    return DataEvent(
                        data['id'],
                        data['login'],
                        data['clan'],
                        data['heal'],
                        data['black'],
                        data['life'],
                        data['pol'],
                        data['age'],
                        data['sound'],
                        data['history'],
                        raw_event_dict=data
                    )
                case CWEventType.UPDATE:
                    if 'dey' in data:
                        return UpdateActionEvent(**data)
                    elif not data:
                        return CWEvent(CWEventType.NO_EVENT)
                    else:
                        return UpdateParametersEvent(
                            data.get('son'),
                            data.get('hunger'),
                            data.get('thirst'),
                            data.get('need'),
                            data.get('health'),
                            data.get('clean'),
                            raw_event_dict=data,
                        )
                case CWEventType.MOVE:
                    if data['x'] == 0 and data['y'] == 0:
                        return CatLeaveEvent(data['id'])
                    else:
                        return MoveEvent(data)
                case CWEventType.LOCATION:
                    return LocationEvent(data['name'], data['bg'])
                case _:
                    return CWEvent(CWEventType.NO_EVENT, raw_message)
        except Exception as exc:
            print(exc)
            print(data)
            return CWEvent(CWEventType.NO_EVENT)


class MessageEvent(CWEvent):
    def __init__(
            self,
            message_id: int,
            text: str,
            cat_id: int,
            time: int,
            volume: int,
            login: str,
            text_transformation: str,
    ):
        super().__init__(CWEventType.MESSAGE)
        self.message_id = message_id
        self.text = text
        self.cat_id = cat_id
        self.time = time
        self.volume = volume
        self.login = login
        self.text_transformation = text_transformation

    def __str__(self):
        return f"[{millis_to_str(self.time)}] {self.login}[{self.cat_id}]({self.volume}): {self.text}"


class MessageLoadEvent(CWEvent):
    def __init__(
            self,
            messages: list[MessageEvent]
    ):
        super().__init__(CWEventType.MESSAGES_LOAD)
        self.messages = messages

    def __str__(self):
        caret_return = '\n'
        return f"Prev messages:\n{caret_return.join([str(message) for message in self.messages])}"


class FieldEvent(CWEvent):
    def __init__(
            self,
            hunt_mode: bool,
            music: str,
            wer: str,
            rotate: int,
            users: dict,
            map_: dict,
            items: dict,
            cats_taken: dict,
            items_taken: dict,
            puddles: dict,
    ):
        super().__init__(CWEventType.FIELD)
        self.hunt_mode = hunt_mode
        self.music = music
        self.wer = wer
        self.rotate = rotate
        self.users = users
        self.map = map_
        self.items = items
        self.cats_taken = cats_taken
        self.items_taken = items_taken
        self.puddles = puddles

    def __str__(self):
        return "FIELD EVENT"


class LocationEvent(CWEvent):
    def __init__(
            self,
            name: str,
            bg: int,
    ):
        super().__init__(CWEventType.LOCATION)
        self.name = name
        self.bg = bg

    def __str__(self):
        return "LOCATION EVENT"


class DataEvent(CWEvent):
    def __init__(
            self,
            cat_id: int,
            name: str,
            clan: ClanEnum,
            heal: int,
            black: int,
            life: int,
            gender: str,
            age: float,
            sound: int,
            history: str,
            raw_event_dict: dict | None = None
    ):
        super().__init__(CWEventType.DATA, raw_event_dict=raw_event_dict)
        self.id = cat_id
        self.name = name
        self.clan = clan
        self.heal = heal
        self.black = black
        self.life = life
        self.gender = gender
        self.age = age
        self.sound = sound
        self.history = history


class UpdateParametersEvent(CWEvent):
    def __init__(
            self,
            son: int | None = None,
            hunger: int | None = None,
            thirst: int | None = None,
            need: int | None = None,
            health: int | None = None,
            clean: int | None = None,
            raw_event_dict: dict | None = None
    ):
        super().__init__(CWEventType.UPDATE, raw_event_dict=raw_event_dict)
        self.dream = son
        self.hunger = hunger
        self.thirst = thirst
        self.need = need
        self.health = health
        self.clean = clean


class UpdateActionEvent(CWEvent):
    def __init__(
            self,
            dey: int | None = None,
            edt: int | None = None,
            mitval: int | None = None,
            raw_event_dict: dict | None = None
    ):
        super().__init__(CWEventType.UPDATE_ACTION, raw_event_dict=raw_event_dict)
        self.action_id = dey
        self.edt = edt
        self.mitval = mitval


class MoveEvent(CWEvent):
    def __init__(
            self,
            cat: dict,
            new_cat: bool | None = None
    ):
        super().__init__(CWEventType.MOVE)
        self.cat = cat
        self.new_cat = new_cat


class CatLeaveEvent(CWEvent):
    def __init__(
            self,
            cat_id: int,
            cat_name: str | None = None
    ):
        super().__init__(CWEventType.LEAVE_LOCATION)
        self.id = cat_id

