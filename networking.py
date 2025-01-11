import json
import datetime
import random
import requests
import websockets


expire_date = datetime.datetime.now() + datetime.timedelta(days=400)


CW_DOMAIN = 'catwar.su'
CW_API = f'https://{CW_DOMAIN}'
CW_LOGIN_API = f'{CW_API}/ajax/login'
CW_SOCKET_IO = f'{CW_API}/ws/cw3/socket.io/?EIO=3&transport=polling'
WSS_API_WO_SID = f'wss://{CW_DOMAIN}/ws/cw3/socket.io/?EIO=3&transport=websocket&sid='

DEFAULT_COOKIE = f'mobile=0; expires=Sun, {expire_date:"%d-%b-%Y %H:%M:%S"} GMT; Max-Age=157680000; HttpOnly'
COMMON_HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'X-Kl-Ajax-Request': 'Ajax_Request',
    'Referer': f'{CW_API}/cw3/',
}
DEFAULT_HEADERS = {
    **COMMON_HEADERS,
    'Priority': 'u=1, i',
    "Sec-Ch-Ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "Windows",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/125.0.0.0 Safari/537.36",
}
WEBSOCKET_HEADERS = {
    **COMMON_HEADERS,
    'Connection': 'Upgrade',
    "Sec-Websocket-Extensions": "permessage-deflate; client_max_window_bits",
    "Sec-Websocket-Version": "13",
    "Upgrade": "websocket",
}


def get_first_cookie_part(login: str, password: str, cat_name: str = '0') -> str:
    resp = requests.post(CW_LOGIN_API, headers=DEFAULT_HEADERS, data={
        'mail': login, 'pass': password, 'cat': cat_name
    })
    cookie = f"{resp.headers['Set-Cookie']}; {DEFAULT_COOKIE}"
    return cookie


def get_socket_sid(cookie: str) -> str:
    resp = requests.get(CW_SOCKET_IO, headers={
        **DEFAULT_HEADERS,
        'Cookie': cookie,
    })
    resp_json = json.loads(resp.text[resp.text.find('{'):])
    sid = resp_json['sid']
    return sid


def get_socket_from_data(sid: str, cookie: str) -> websockets.connect:
    wss_api_w_sid = f'{WSS_API_WO_SID}{sid}'
    return websockets.connect(wss_api_w_sid, extra_headers={
        **WEBSOCKET_HEADERS,
        'Cookie': cookie,
    })


def login_and_receive_socket(login: str, password: str, cat_name: str = '0') -> websockets.connect:
    cookie = get_first_cookie_part(login, password, cat_name)
    sid = get_socket_sid(cookie)
    websocket = get_socket_from_data(sid, cookie)
    return websocket


if __name__ == '__main__':
    from config import config
    cookie_ = get_first_cookie_part(config['login'], config['password'], config['my_cat'])
    sid_ = get_socket_sid(cookie_)
    print(cookie_)
    print(f'{WSS_API_WO_SID}{sid_}')
