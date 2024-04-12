from datetime import datetime
import json
import requests
from requests.exceptions import HTTPError
import repo_config


def get_rates(codes_crypto):
    """ Gets crypto to USD rates from pro-api.coinmarketcap.com, returns [...rates]
    WARN! returns only items that were successfully fetched
    >>> get_rates(["USDT", "BTC"])
    '([{"from": "USDT","to": "USD","rate": 1,"updatedAt": "2024-03-27 16:17:23"}], "")'
    (suppose that in example above we've failed to fetch BTC price)
    """

    api_token, err_msg = repo_config.get_cmc_api_token()
    if err_msg != "":
        return [], f"failed to get rates: {err_msg}"

    session = requests.Session()
    session.headers.update({
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_token,
    })

    params = {
        'symbol': ','.join(codes_crypto)
    }

    try:
        response = session.get("https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest", params=params)
        response.raise_for_status()
    except HTTPError as http_err:
        return [], f"HTTP error occurred: {http_err}"
    except Exception as err:
        return [], f"Other error occurred: {err}"
    else:
        resp = json.loads(response.text)

        rates = []
        for code in resp['data']:

            rates.append({
                "from": code,
                "to": "USD",
                "rate": resp['data'][code][0]['quote']['USD']['price'],
                "updatedAt": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

        return rates, ''


if __name__ == '__main__':
    try:
        print(get_rates(["USDT", "BTC"]))
    except KeyboardInterrupt:
        print(f"KeyboardInterrupt, exiting ...")
        quit(0)
