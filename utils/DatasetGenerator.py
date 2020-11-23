from random import randint, choice, randrange
from string import ascii_lowercase
from datetime import datetime, timedelta


def random_dataset():
    dataset = {
        "id": _random_str(),
        "ods_domain": _random_iri(),
        "metas": {
            'default': {
                "title": _random_str(),
                "language": "en",
                "modified": _random_date()
            },
            "dcat": {
                "created": _random_date(),
                "issued": _random_date(),
                "creator": _random_str(),
                "contributor": _random_str(),
                "contact_name": _random_str(),
                "contact_email": _random_iri(),
                "accrualperiodicity": _random_str()
            }
        }
    }
    return dataset


def _random_str():
    length = randint(5, 20)
    letters = ascii_lowercase
    return ''.join(choice(letters) for i in range(length))


def _random_iri():
    base = _random_str()
    path = _random_str()
    return f"https://www.{base}/{path}"


def _random_date():
    start = datetime.strptime('1/1/2012', '%d/%m/%Y')
    end = datetime.strptime('1/1/2020', '%d/%m/%Y')
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    date = start + timedelta(seconds=random_second)
    return date.strftime("%d/%m/%Y")
