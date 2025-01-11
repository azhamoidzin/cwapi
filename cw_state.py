from cw_events import FieldEvent, DataEvent, UpdateParametersEvent, MoveEvent, CatLeaveEvent, LocationEvent
from cw_cat import PlayerCat, Parameters
from junk.clan_enum import ClanEnum


class Portal:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Cat:
    def __init__(
            self,
            cat_id: int,
            login: str,
            clan: ClanEnum,
            gender: str,
            online: str,
            mode: int,
            a_act: int,
            clan_position: str,
    ):
        self.cat_id = cat_id
        self.login = login
        self.clan = clan
        self.gender = gender
        self.online = online
        self.mode = mode
        self.a_act = a_act
        self.clan_position = clan_position

    def __str__(self):
        return f"{self.login}[{self.cat_id}]"

    def __repr__(self):
        return self.__str__()


class Item:
    def __init__(self, item_type: int, unique_id: int):
        self.item_type = item_type
        self.unique_id = unique_id

    def __str__(self):
        return f"[{self.item_type}] (id: {self.unique_id})"


class Cell:
    CELL_W_PX = 100
    CELL_H_PX = 167

    def __init__(
            self,
            x: int,
            y: int,
            cat: Cat | None = None,
            items: list[Item] | None = None,
            portal: Portal | None = None,
    ):
        self.x = x
        self.y = y
        self.cat = cat
        self.items = items
        if not items:
            self.items = []
        self.portal = portal

    def __str__(self):
        # cell_base = f"[{self.x}, {self.y}]"
        cell_base = f""
        if self.portal:
            cell_base = f"{cell_base}({self.portal})"
        if self.cat:
            cell_base = f"{cell_base}{self.cat}"
        if self.items:
            cell_base = f"{cell_base} ({len(self.items)})"
        return cell_base

    def __repr__(self):
        return self.__str__()


class Field:
    MAX_CELL_LEN_SYMBOLS = 25
    cats_dict: dict[int, list[str, int, int]] = {}
    location: str = ''

    def __init__(
            self,
            cells: list[list[Cell]],
            hunt_mode: bool,
            music: str,
            wer: str,
            rotate: int,
    ):
        self.hunt_mode = hunt_mode
        self.music = music
        self.wer = wer
        self.rotate = rotate
        self.cells = cells

    def __getitem__(self, index):
        return [row[index] for row in self.cells]

    def __str__(self):
        rows = []
        for row in self.cells[1:]:
            row_str = " | ".join(
                (str(cell)[:self.MAX_CELL_LEN_SYMBOLS - 3] + '...' if len(str(cell)) > self.MAX_CELL_LEN_SYMBOLS
                 else str(cell))
                .center(self.MAX_CELL_LEN_SYMBOLS) for cell in row[1:])
            rows.append(row_str)
        return ('\n' + ('-' * (self.MAX_CELL_LEN_SYMBOLS + 3)) * 10 + '\n').join(rows)

    @classmethod
    def from_event(cls, field_event: FieldEvent):
        cls.cats_dict = {}
        hunt_mode = field_event.hunt_mode
        music = field_event.music
        wer = field_event.wer
        rotate = field_event.rotate
        field = [[Cell(y, x) for y in range(11)] for x in range(7)]

        # iterate cats
        for col_idx, cats in field_event.users.items():
            col_idx = int(col_idx)
            cats: list
            for row_idx, cat in enumerate(cats):
                if cat:
                    field[row_idx][col_idx].cat = Cat(
                        cat['id'],
                        cat['login'],
                        cat['clan'],
                        cat['pol'],
                        cat['online'],
                        cat['mode'],
                        cat['aAct'],
                        cat['clan_position'],
                    )
                    cls.cats_dict[cat['id']] = [cat['login'], col_idx, row_idx]
        print(cls.cats_dict)
        # iterate portals
        for col_idx, portals in field_event.map.items():
            col_idx = int(col_idx)
            portals: list
            for row_idx, portal in enumerate(portals):
                if portal:
                    field[row_idx][col_idx].portal = Portal(portal['name'])

        # iterate items
        for col_idx, items in field_event.items.items():
            col_idx = int(col_idx)
            items: list
            for row_idx, items_list in enumerate(items):
                if items_list:
                    field[row_idx][col_idx].items = [Item(item['type'], item['id']) for item in items_list]

        return cls(field, hunt_mode, music, wer, rotate)
        # for col_idx, portal in raw_data['map']:


class CWState:
    def __init__(self):
        self.field: Field | None = None
        self.my_cat: PlayerCat | None = None

    def update_field_from_event(self, field_event: FieldEvent):
        self.field = Field.from_event(field_event)
        print(self.field)

    def update_location_from_event(self, location_event: LocationEvent):
        self.field.location = location_event.name
        print(self.field.location)

    def set_player_cat_from_event(self, data_event: DataEvent):
        self.my_cat = PlayerCat(
            data_event.id,
            data_event.name,
            data_event.gender,
            data_event.clan,
            **{
                'black': data_event.raw_event_dict['black'],
                'life': data_event.raw_event_dict['life'],
                'history': data_event.raw_event_dict['history'],

                'power': data_event.raw_event_dict['power'],
                'dig': data_event.raw_event_dict['dig'],
                'swim': data_event.raw_event_dict['swim'],
                'observ': data_event.raw_event_dict['observ'],
                'tree': data_event.raw_event_dict['tree'],
                'smell': data_event.raw_event_dict['smell'],
                'heal': data_event.raw_event_dict['heal'],
                'might': data_event.raw_event_dict['might'],
                'pet_faith': data_event.raw_event_dict['pet_faith'],

            },
        )
        print(self.my_cat.full_info())

    def update_player_cat_from_event(self, update_event: UpdateParametersEvent):
        if self.my_cat:
            self.my_cat.parameters = Parameters(**update_event.raw_event_dict)
            print(self.my_cat.full_info())

    def remove_cat_from_field(self, leave_location: CatLeaveEvent) -> str:
        cat_name, x, y = self.field.cats_dict.pop(leave_location.id)
        self.field[x][y].cat = None
        return cat_name

    def move_cat_from_event(self, move_event: MoveEvent) -> bool:
        cat = move_event.cat
        cat_obj = Cat(
            cat['id'],
            cat['login'],
            cat['clan'],
            cat['pol'],
            cat['online'],
            cat['mode'],
            cat['aAct'],
            cat['clan_position'],
        )
        x: int
        y: int
        x, y = move_event.cat['x'], move_event.cat['y']

        if move_event.cat['id'] in self.field.cats_dict:
            old_x, old_y = self.field.cats_dict[move_event.cat['id']][1:]
            self.field[x][y].cat = cat_obj
            self.field[old_x][old_y].cat = None
            new_cat = False
        else:
            self.field[x][y].cat = cat_obj
            self.field.cats_dict[move_event.cat['id']] = [cat_obj.login, x, y]
            new_cat = True
        return new_cat


cw_state = CWState()

# field = Field(3, 3)
#
#
# print(field)
