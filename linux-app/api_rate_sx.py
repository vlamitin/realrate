import asyncio
from datetime import datetime

import requests
from requests.exceptions import HTTPError


def get_rates(codes_crypto):
    """ Gets crypto to USD rates from rate.sx, returns [...rates]
    WARN! returns only items that were successfully fetched
    >>> get_rates(["USDT", "BTC"])
    '[{"from": "USDT","to": "USD","rate": 1,"updatedAt": "2024-03-27 16:17:23"}]'
    (suppose that in example above we've failed to fetch BTC price)
    """
    results = asyncio.get_event_loop().run_until_complete(_async_get_http_results(codes_crypto))

    rates = []
    for i in range(len(codes_crypto)):
        if results[i][1] != "":
            continue

        rates.append({
            "from": codes_crypto[i],
            "to": "USD",
            "rate": float(results[i][0]),
            "updatedAt": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    return rates


async def _async_get_http_results(codes_crypto):
    loop = asyncio.get_event_loop()

    futures = [loop.run_in_executor(None, _http_get, f"http://rate.sx/1{code}") for code in codes_crypto]
    return [await x for x in futures]


def _http_get(url_str):
    """returns (responseText<str>, err_msg)
    """
    try:
        response = requests.get(url_str)
        response.raise_for_status()
    except HTTPError as http_err:
        return "", f"HTTP error occurred: {http_err}"
    except Exception as err:
        return "", f"Other error occurred: {err}"
    else:
        return response.text, ""


if __name__ == '__main__':
    try:
        print(get_rates(["USDT", "BTC"]))
    except KeyboardInterrupt:
        print(f"KeyboardInterrupt, exiting ...")
        quit(0)
