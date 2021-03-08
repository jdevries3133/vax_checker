import logging
from typing import Union, List

from teacherHelper import Email

logger = logging.getLogger(__name__)

def email(addr: Union[str, List[str]], avail: list, storename: str) -> None:
    """
    Support sending to an individual or to a list of people.
    """
    logger.info('Appointment(s) found')
    logger.debug(
        f'Sending emails to {addr} with message {avail} for {storename}'
    )
    with Email() as emlr:
        if isinstance(addr, str):
            emlr.send(
                to=addr,
                subject=f'{storename} Vaccine Available',
                message=(
                    [
                        f'{storename} vaccine appointments are available now at '
                        'the following locations:'
                    ]
                    + ['- ' + i for i in avail]
                )
            )
        else:
            for address in addr:
                emlr.send(
                    to=address,
                    subject=f'{storename} Vaccine Available',
                    message=(
                        [
                            f'{storename} vaccine appointments are available now at '
                            'the following locations:'
                         ]
                        + ['- ' + i for i in avail]
                    )
                )
