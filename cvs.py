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

import requests

from common import email
from settings import EMAIL_TO

URLS = {
    'endpoint': (
        'https://www.cvs.com/immunizations/covid-19-vaccine.vaccine-status.NJ.json'
        '?vaccineinfo'
    ),
    'referer': 'https://www.cvs.com/immunizations/covid-19-vaccine'
}
SCRIPT_USER_AGENT = (
    'Python_Requests Vaccine_Availability_Monitor_Bot'
)
POLL_INTERVAL = 60  # seconds

def is_successful(request):
    return True if 200 <= request.status_code <= 299 else False

class CVSApiException(Exception):
    pass

def get_data() -> Union[dict, None]:
    """
    Get NJ covid vaccine data.
    """
    ses = requests.Session()
    res = ses.get(URLS['referer'])
    ses.headers.update({
        'referer': URLS['referer'],
        'User-Agent': SCRIPT_USER_AGENT,
        'content-type': 'application/json',
    })
    res = ses.get(URLS['endpoint'])
    if is_successful(res):
        return res.json()
    else:
        raise CVSApiException('Uncessful response from server')

def available_appts(data) -> list:
    return [
        l['city'].title() for l in data['responsePayloadData']['data']['NJ']
        if l['status'].lower() != 'fully booked'
    ]

def check(email_to: Union[str, List[str]]):
    data = get_data()
    if data:
        locs = available_appts(data)
        if locs:
            email(
                EMAIL_TO,
                locs,
                'CVS'
            )
            # success! Wait an hour as to not harrass subscribers
            sleep(3600)

if __name__ == '__main__':
    check('jdevries3133@gmail.com')
