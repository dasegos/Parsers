import requests
from requests import Response
from requests.status_codes import codes

import os
from dotenv import load_dotenv

from utils import login, switch_to_db, switch_to_users_table, parse_database, print_data


load_dotenv()

USERNAME=os.getenv('USERNAME')
PASSWORD=os.getenv('PASSWORD')


def get_database_data(include_params: bool = False):
    session = requests.Session() # creating a session instance that will be used throughout the program
    auth_response: Response = login(session, USERNAME, PASSWORD, 'http://185.244.219.162/phpmyadmin/index.php', include_params) # trying to login

    # authentication successful
    if auth_response.status_code == codes['OK'] and 'pmaUser-1' in auth_response.cookies.keys() and 'pmaAuth-1' in auth_response.cookies.keys():
        print('Authentication successful!')

        if include_params: # parsing all data immediately if include_params equals to True
            data = parse_database(auth_response.text)
            print_data(data)
            print()

        else: # otherwise switching between pages
            database_link = switch_to_db(auth_response.text, 'testDB')
            database_page = session.get(f'http://185.244.219.162/phpmyadmin/{database_link}')
            users_link = switch_to_users_table(database_page.text)
            users_page = session.get(f'http://185.244.219.162/phpmyadmin/{users_link}')
            data = parse_database(users_page.text)
            print_data(data)
            print()

    # something went wrong    
    elif auth_response.status_code == codes['OK']:
        print('❌ Authentication failed, but no errors occurred.\n It must be something wrong with auth details!')

    else:
        print(f'⚠️ Authentication failed with status code {auth_response.status_code}')


if __name__ == '__main__':
    options = '\n1. Перейти на страницу базы данных сразу;\n2. Войти в аккаунт на начальную страницу и самостоятельно перейти на страницу с базой;\n'
    print(options)
    while True:
        option_input = input('Выберите способ из предложенного списка: \n')
        match option_input:
            case '1':
                get_database_data(True)
                exit()
            case '2':
                get_database_data()
                exit()
            case _:
                print('Такого способа не существует!')
