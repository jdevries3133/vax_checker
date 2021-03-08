from cvs import check as cvs_check
from rite_aid import check as rita_aid_check
from settings import EMAIL_TO

if __name__ == '__main__':
    while True:
        cvs_check(EMAIL_TO)
        rita_aid_check(EMAIL_TO)
