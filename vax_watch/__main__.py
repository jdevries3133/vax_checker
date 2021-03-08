import logging

from .cvs import check as cvs_check
from .rite_aid import check as rita_aid_check
from .settings import EMAIL_TO

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[logging.StreamHandler()],
    format='%(pathname)s:%(lineno)s\n\t%(module)s::%(message)s'
)

while True:
    cvs_check(EMAIL_TO)
    rita_aid_check(EMAIL_TO)
