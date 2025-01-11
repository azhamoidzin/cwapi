import asyncio
import json
from typing import Union
import cw_exceptions
from cw_constants import CWConstants
from networking import login_and_receive_socket
from cw_event_type import CWCommandType, CWActionType
from cw_movement import CWMove, CWMoveSequence
from cw_events import CWEvent, CWEventType
from cw_state import cw_state, Cell


class CWAPI:
    def __init__(
            self,
            login: str,
            password: str,
            cat_name: str = '0',
            command_interval_ms: int = CWConstants.DEFAULT_COMMAND_INTERVAL_MS
    ):
        self.ws = login_and_receive_socket(login, password, cat_name)
        self.interval = command_interval_ms
        self.state = cw_state

    async def __aenter__(self):
        self.cw_client = await self.ws.__aenter__()
        await self._handshake()
        self.ping_task = asyncio.create_task(self._ping_w_interval())
        await self.first()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cw_client.close()

    async def _ping_w_interval(self):
        while True:
            await self.cw_client.send("2")
            await asyncio.sleep(20)

    async def _handshake(self):
        await self.cw_client.send('2probe')
        message = await self.cw_client.recv()
        if message == '3probe':
            await self.cw_client.send('5')
            message = await self.cw_client.recv()
            if message == '40':
                message = await self.cw_client.recv()
                if message == '42["was connected",null]':
                    return
                else:
                    raise cw_exceptions.FailedSocketHandshakeException(f'Did not receive '
                                                                       f'"42["was connected",null]" after "40". '
                                                                       f'Got: {message}')
            else:
                raise cw_exceptions.FailedSocketHandshakeException('Did not receive "40" after "5"')
        else:
            raise cw_exceptions.FailedSocketHandshakeException('Did not receive "3probe" after "2probe"')

    async def _perform_command(self, command: CWCommandType, data=None):
        try:
            if data:
                print(f'42["{command}", {json.dumps(data)}]')
                await self.cw_client.send(f'42["{command}", {json.dumps(data)}]')
            else:
                print(f'42["{command}", {json.dumps(data)}]')
                await self.cw_client.send(f'42["{command}"]')
            await asyncio.sleep(self.interval // 1000)
        except Exception as exc:
            raise cw_exceptions.ExecuteCommandException(f"Failed to execute {command}: {exc}")

    def _perform_cat_action(self, action: CWActionType, act_with_id: int = 0):
        return self._perform_command(CWCommandType.ACTION, {'id': action, 'actWith': act_with_id})

    @staticmethod
    def generate_event_from_message(raw_message: str) -> CWEvent:
        print(f'Raw message: {raw_message}')
        return CWEvent.from_raw_message(raw_message)

    async def first(self):
        return await self._perform_command(CWCommandType.FIRST)

    async def send_message(self, message: str, volume: int = CWConstants.DEFAULT_MESSAGE_VOLUME):
        return await self._perform_command(CWCommandType.MSG, {'text': message, 'volume': volume})

    async def listen(self):
        while True:
            message = await self.cw_client.recv()
            if message in ['3', '3probe', '40']:
                continue
            event = self.generate_event_from_message(message)
            if event.event_type == CWEventType.MESSAGE:
                pass
            if event.event_type == CWEventType.FIELD:
                self.state.update_field_from_event(event)
            if event.event_type == CWEventType.LOCATION:
                self.state.update_location_from_event(event)
            if event.event_type == CWEventType.DATA:
                self.state.set_player_cat_from_event(event)
            if event.event_type == CWEventType.UPDATE:
                self.state.update_player_cat_from_event(event)
            if event.event_type == CWEventType.LEAVE_LOCATION:
                cat_name = self.state.remove_cat_from_field(event)
                event.cat_name = cat_name
            if event.event_type == CWEventType.MOVE:
                new_cat = self.state.move_cat_from_event(event)
                event.new_cat = new_cat
            yield event

    async def move(self, move: Union[CWMove, CWMoveSequence, Cell]):
        if isinstance(move, Cell):
            move = CWMove.from_cell(move)
        if isinstance(move, CWMove):
            return await self._perform_command(CWCommandType.MOVE, move.as_dict())
        if isinstance(move, CWMoveSequence):
            for move_el in move:
                await self._perform_command(CWCommandType.MOVE, move_el.as_dict())
                await asyncio.sleep(move.interval_w_delta // 1000)

    async def start_block(self):
        return await self._perform_command(CWCommandType.FIGHT_BLOCK, True)

    async def stop_block(self):
        return await self._perform_command(CWCommandType.FIGHT_BLOCK, False)

    async def start_rotate(self, direction: bool = False):
        return await self._perform_command(CWCommandType.START_ROTATE, direction)

    async def stop_rotate(self):
        return await self._perform_command(CWCommandType.STOP_ROTATE)

    async def fight_attack(self, attack_type: bool):
        return await self._perform_command(CWCommandType.FIGHT_ATTACK, attack_type)

    async def cancel(self):
        return await self._perform_cat_action(CWActionType.CANCEL)

    async def sleep(self):
        return await self._perform_cat_action(CWActionType.SLEEP)

    async def smell(self, cat_id: int = None):
        if not cat_id:
            return await self._perform_cat_action(CWActionType.SMELL_SELF)
        return await self._perform_cat_action(CWActionType.SMELL_CAT, cat_id)

    async def enter_combat_mode(self):
        return await self._perform_cat_action(CWActionType.ENTER_COMBAT)

    async def exit_combat_mode(self):
        return await self._perform_cat_action(CWActionType.EXIT_COMBAT)

    async def lick(self, cat_id: int = None):
        if not cat_id:
            return await self._perform_cat_action(CWActionType.LICK_SELF)
        return await self._perform_cat_action(CWActionType.LICK_CAT, cat_id)

    async def cheek(self, cat_id: int):
        return await self._perform_cat_action(CWActionType.CHEEK_CAT, cat_id)

    async def dig(self):
        return await self._perform_cat_action(CWActionType.DIG)
