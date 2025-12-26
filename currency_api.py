from typing import List, Dict
import requests

from config import API_KEY
from currencies import CURRENCIES



BASE_URL = 'https://www.amdoren.com/api/currency.php'

def get_currencies() -> List[str]:
    return [
        '{code}: {name}'.format(code=currency_code, name=currency_name)
        for currency_code, currency_name in CURRENCIES.items()
    ]

def convert_currency(convert_from: str, convert_to: str, amount: float) -> Dict:
    """API request"""
    responce = requests.get(f'{BASE_URL}', params={
        'api_key': API_KEY,
        'from': convert_from,
        'to': convert_to,
        'amount': amount
    })
    return responce.json()

