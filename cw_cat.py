from junk.enums import ClanEnum, GenderEnum


class Skills:
    def __init__(self, **kwargs):
        self.bu: int = kwargs['power']
        self.ku: int = kwargs['dig']
        self.pu: int = kwargs['swim']
        self.zu: int = kwargs['observ']
        self.lu: int = kwargs['tree']
        self.nu: int = kwargs['smell']
        self.cu: int = kwargs['heal']
        self.mu: int = kwargs['might']
        self.vd: int = kwargs['pet_faith']

    def __str__(self):
        return (f" БУ: {self.bu}\n КУ: {self.ku}\n ПУ: {self.pu}\n ЗУ: {self.zu}\n ЛУ: {self.lu}\n НУ: {self.nu}\n "
                f"Верность двуногим  : {self.vd}\n Могущество         : {self.mu}\n Целительские умения: {self.cu}\n")


class Parameters:
    def __init__(self, **kwargs):
        self.dream: int = -kwargs.get('dream') if kwargs.get('dream') else None
        self.thirst: int = -kwargs.get('thirst') if kwargs.get('thirst') else None
        self.hunger: int = -kwargs.get('hunger') if kwargs.get('hunger') else None
        self.need: int = kwargs.get('need')
        self.health: int = kwargs.get('health')
        self.clean: int = kwargs.get('clean')

    def __str__(self):
        return (f" Сон: {self.dream}\n Голод: {self.hunger}\n Жажда: {self.thirst}\n"
                f" Нужда: {self.need}\n Чистота: {self.clean}\n Здоровье: {self.health}\n")

class CatBase:
    def __init__(self, cat_id: int, name: str, gender: GenderEnum, clan: ClanEnum):
        self.id = cat_id
        self.name = name
        self.gender = gender
        self.clan = clan

    def __eq__(self, other):
        if isinstance(other, CatBase):
            return self.id == other.id and self.name == other.name
        else:
            raise NotImplementedError


class PlayerCat(CatBase):
    def __init__(
            self,
            cat_id: int,
            name: str,
            gender: GenderEnum | str,
            clan: ClanEnum,
            **kwargs,
    ):
        super().__init__(cat_id, name, gender, clan)

        self.n_black_points: int = kwargs['black']
        self.n_lives: int = kwargs['life']
        self.history: str = kwargs['history']

        self.skills = Skills(**kwargs)
        self.parameters = Parameters(**kwargs)

        self.love_list = []

        self.items = []

    def full_info(self):
        return (f"{self.name}[{self.id}]:\n"
                f"{self.parameters}"
                f"{self.skills}")
