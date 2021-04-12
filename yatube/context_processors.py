import datetime as dt
from typing import Dict

from django.http import HttpRequest


def year(request: HttpRequest) -> Dict[str, int]:
    """Return year."""
    calculated_year = dt.datetime.now().year
    return {
        'year': calculated_year,
    }
