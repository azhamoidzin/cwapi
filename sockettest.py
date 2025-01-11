import asyncio
from cwapi import CWAPI
from config import config
from cw_events import CWEventType
from db_utils import location_log
from datetime import datetime
import requests


def send_tg(message):
    url = f"https://api.telegram.org/bot{config['tg_token']}/sendMessage?chat_id={config['tg_channel']}&text={message}"
    print(requests.get(url).json())  # this sends the message


async def send_and_receive():
    async with CWAPI(config['login'], config['password'], config['my_cat'], 3000) as cwapi:
        # Task to send messages asynchronously
        async def receive_messages():
            async for event in cwapi.listen():
                now = datetime.now()
                if event.event_type == CWEventType.LEAVE_LOCATION:
                    msg = f"{event.cat_name}[{event.id}] покинул(а) локацию {cwapi.state.field.location}"
                    print(msg)
                    send_tg(msg)
                    location_log(now, event.cat_name, event.id, False, cwapi.state.field.location)
                if event.event_type == CWEventType.MOVE:
                    if event.new_cat:
                        msg = f"{event.cat['login']}[{event.cat['id']}] перешел(а) на локацию {cwapi.state.field.location}"
                        print(msg)
                        send_tg(msg)
                        location_log(now, event.cat['login'], event.cat['id'], True, cwapi.state.field.location)

        # Run both tasks concurrently
        await asyncio.gather(receive_messages())


if __name__ == "__main__":
    asyncio.run(send_and_receive())
