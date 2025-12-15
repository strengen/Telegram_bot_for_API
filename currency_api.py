from typing import Set, Dict
import requests
import json


from config import API_KEY
from currencies import CURRENCIES



BASE_URL = 'https://www.amdoren.com/api/currency.php'

def get_currencies() -> Set[str]:
    """List of supported currencies"""
    responce = set(CURRENCIES.keys())
    return responce

def convert_currency(convert_from: str, convert_to: str, amount: float) -> Dict:
    """API request"""
    responce = requests.get(f'{BASE_URL}', params={
        'api_key': API_KEY,
        'from': convert_from,
        'to': convert_to,
        'amount': amount
    })
    return responce.json()

