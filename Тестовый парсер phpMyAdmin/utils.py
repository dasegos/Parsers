import bs4
from requests import Response, Session

from typing import Optional


DEFAULT_USER_AGENT: str = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3.1 Safari/605.1.15'


def login(session: Session, username: str, password: str, url: str, include_params:  bool = False, user_agent: str = DEFAULT_USER_AGENT) -> Response:
    '''
       The function logins to phpMyAdmin using `requests`. 

       Parameters
       ----------
       session        : `Session`, required (`requests.Session` instance)\n
       username       : `str`, required (username to phpMyAdmin admin-panel)\n 
       password       : `str`, required (password to phpMyAdmin admin-panel)\n 
       url            : `str`, required (url to login page)\n
       include_params : `bool`, not required (determines if we will be redirected to a database table page immediately) = `false`\n
       user_agent     : `str`, not required (software that acts on behalf of a user)\n = `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3.1 Safari/605.1.15`

       Returns
       ----------
       auth_response : `Response`
    '''
    response = session.get(url, headers={'User-Agent' : user_agent})
    token = get_input_token(response.text)
    session.headers.update({'User-Agent' : user_agent}) # updating request headers so that a browser doesn't think we are a robot
    params = None # setting params to None if we don't want to receive database table page immediately
    if include_params:
        params = {'route' : '/sql', 'server' : 1, 'db' : 'testDB', 'table' : 'users'}
    auth_response = session.post(url, 
                                 params=params,
                                 data={'token' : token, 'pma_username' : username, 'pma_password' : password})
    return auth_response


def get_input_token(html: str) -> Optional[str]:
    '''
       The function searches for a hidden token in HTML
       content if such exists in order to pass it to 
       POST-request.
     
       Parameters
       ----------
       html : `str`, required\n

       Returns
       ----------
       token : `str` | `None` if specified "path" for a token is changed or doesn't exist
    '''
    soup = bs4.BeautifulSoup(html, 'html.parser')
    token = soup.find('input', {'name': 'token'})
    if token:
        return token['value']
    return None


def switch_to_db(html: str, a_inner: str) -> Optional[str]:
    '''
       The function finds a database link by its inner string content.

       Parameters
       ----------
       html    : `str`, required\n    
       a_inner : `str`, required (usually a database name)\n

       Returns
       ----------
       link : `str` | `None` if specified "path" for a token is changed or doesn't exist
    '''
    soup = bs4.BeautifulSoup(html, 'html.parser')
    link = soup.find('a', string=a_inner)
    if link:
        return link.get('href')
    return None


def switch_to_users_table(html: str) -> Optional[str]:
    '''
       The function finds a link to users table.

       Parameters
       ----------
       html    : `str`, required\n    

       Returns
       ----------
       link : `str` 
    ''' 
    soup = bs4.BeautifulSoup(html, 'html.parser')
    link = soup.find('tr', {'id' : 'row_tbl_1'}).th.a
    if link:
        return link.get('href')
    return None


def parse_database(html: str) -> Optional[list[tuple[int, str]]]:
    '''
       The function parses html page with a database table,
       extracting all `td`s from it.\n
       It writes all tds with data-type "int" to `ids`,
       and all tds with data-type "str" to `names`.
     
       Parameters
       ----------
       html : `str`, required\n

       Returns
       ----------
       data : `list[tuple[int, str]]`
    '''
    soup = bs4.BeautifulSoup(html, 'html.parser')
    try:
        ids = [id_.text for id_ in soup.find_all('td', {'class' : 'data', 'data-type' : 'int'})]
        names = [name.text for name in soup.find_all('td', {'class' : 'data', 'data-type' : 'blob'})]
    except Exception:
        return None
    else:
        return list(zip(ids, names)) # combining two lists into a list of tuples for convenience


def print_data(data: list[tuple[int, str]]) -> None:
    '''
       The function displays a list of tuples in a nice readable way.

       Parameters
       ----------
       data : `list[tuple[int, str]]`, required\n

       Returns
       ----------
       `None`
    '''
    print('\nid | name')
    print('----------')
    for item in data:
        print(*item) # "unpacking a tuple"
