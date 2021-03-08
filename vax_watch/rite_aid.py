"""
Script to check for available vaccines at CVS in the State of New Jersey,
although it will presumably work nationally by simply changing the API
endpoint at the top of the script.

**teacherHelper dependency**

I use my own home-grown teacherHelper module which has a built in abstraction
on top of python's smtlib to send emails here. If you want to use this,
you will need to add that bit yourself.
"""

from typing import Union, List
from time import sleep
import logging

import requests

from .common import email
from .settings import LOCATION_SEARCH_QUERY, MILES_RADIUS

logger = logging.getLogger(__name__)

URLS = {
    'initial': 'https://www.riteaid.com/pharmacy/apt-scheduler',
    'getStores': {
        'href': 'https://www.riteaid.com/services/ext/v2/stores/getStores',
        'params': {
            'address': 'Jersey City',  # query string. can be city name.

            # I think this is the special service key for locations with covid
            # vaccines
            'attrFilter': 'PREF-112',

            'fetchMechanismVersion': 2,
            'radius': 50  # miles
        }
    },
    'checkSlots': {  # for a given store
        'href': 'https://www.riteaid.com/services/ext/v2/vaccine/checkSlots',
        'params': {
            'storeNumber': int  # coming from getStores
        }
    }
}
SCRIPT_USER_AGENT = (
    'Python_Requests Vaccine_Availability_Monitor_Bot'
)
POLL_INTERVAL = 60  # seconds

def is_successful(request: requests.Response) -> bool:
    return True if 200 <= request.status_code <= 299 else False

class CVSApiException(Exception):
    pass

def get_session() -> requests.Session:
    """
    Establish session and cookies
    """
    session = requests.Session()
    session.get(URLS['initial'])
    return session

def get_stores(address_query: str, mi_radius: int) -> Union[dict, None]:

    session = get_session()

    # prepare params
    params = {
        **URLS['getStores']['params'],
        'address': address_query,
        'radius': mi_radius,
    }

    # get stores
    res = session.get(URLS['getStores']['href'], params=params)
    if is_successful(res):
        return res.json()['Data']['stores']
    else:
        logger.error('Unsuccessful response from Rite Aid backend')

def find_available_appts(stores: Union[dict, None]) -> List[dict]:
    if not stores:
        return []
    session = get_session()
    locs = []
    for store in stores:
        res = session.get(
            URLS['checkSlots']['href'],
            params={'storeNumber': store['storeNumber']},
        )
        if is_successful(res):
            for slot in res.json()['Data']['slots'].values():
                if slot:
                    logger.info(f'Slot available in {store["city"]}')
                    locs.append(store)
                else:
                    logger.debug(f'Slot not available in {store["city"]}')
    return locs

def email_fmt(locs: List[dict]) -> List[str]:

    out = []
    for loc in locs:
        out += [
            loc['name'],
            loc['address'],
            f'{loc["city"]}, {loc["state"]} {loc["zipcode"]}',
            '\n'
        ]
    return out

def check(email_to: Union[str, List[str]]):
    """
    Check for appointments, send an email if one is found.
    """
    stores = get_stores(LOCATION_SEARCH_QUERY, MILES_RADIUS)
    locs = find_available_appts(stores)
    formatted = email_fmt(locs)
    if formatted:
        email(email_to, formatted, 'Rite Aid')
        sleep(3600)

if __name__ == '__main__':
    check('jdevries3133@gmail.com')
