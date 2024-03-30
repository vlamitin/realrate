import asyncio
import datetime
import json
import requests
from requests.exceptions import HTTPError
import repo_config


# TODO replace with some more useful grouping
def to_request_dict(codes_fiat):
    """
    >>> to_request_dict(["USD", "EUR", "KZT", "RUB", "TRY", "RSD", "CAD", "CHF", "NZD", "JPY"])
    '{"USD": {"EUR", "KZT", "RUB", "TRY", "RSD", "CAD", "CHF", "NZD", "JPY"}, {"CAD": {"CHF"}}, {"JPY":{"CHF"}}}'
    """
    api_requests_limit = 3
    # top_traded_pairs = [
    #     {"EUR", "USD"}, {"USD", "JPY"}, {"GBP", "USD"}, {"AUD", "USD"}, {"USD", "CAD"}, {"USD", "CHF"}, {"NZD", "USD"},
    #     {"EUR", "JPY"}, {"GBP", "JPY"}, {"EUR", "GBP"}, {"AUD", "JPY"}, {"EUR", "AUD"}, {"EUR", "CHF"}, {"AUD", "NZD"},
    #     {"NZD", "JPY"}, {"GBP", "AUD"}, {"GBP", "CAD"}, {"EUR", "NZD"}, {"AUD", "CAD"}, {"GBP", "CHF"}, {"AUD", "CHF"},
    #     {"EUR", "CAD"}, {"CAD", "JPY"}, {"GBP", "NZD"}, {"CAD", "CHF"}, {"CHF", "JPY"}, {"NZD", "CAD"}, {"NZD", "CHF"},
    # ]
    top_mediators = ["USD", "EUR", "JPY", "GBP", "AUD", "CHF", "CAD"]

    graph = {}
    for code in codes_fiat:
        codes_set = set(codes_fiat)
        codes_set.remove(code)
        graph[code] = codes_set

    requests_dict = {}
    for i in range(api_requests_limit):
        if i == api_requests_limit - 1:
            if top_mediators[0] not in requests_dict:
                codes_set = set(codes_fiat)
                if top_mediators[0] in codes_set:
                    codes_set.remove(top_mediators[0])
                requests_dict[top_mediators[0]] = codes_set
                break
        requests_dict[codes_fiat[i]] = graph[codes_fiat[i]]

    return requests_dict

def get_rates_fiat(codes_fiat):
    """ Gets fiat rates from currencybeacon.com, returns ([...rates], err_msg)
    WARN! returns only items that were successfully fetched
    >>> get_rates_fiat(["USD", "EUR", "KZT"])
    '([{"from": "USD","to": "KZT","rate": 449.836,"updatedAt": "2024-03-27T16:17:23.556Z"}], "")'
    (suppose that in example above we've failed to fetch USD to EUR and EUR to KZT prices)
    """
    api_token, err_msg = repo_config.get_cb_api_token()
    if err_msg != "":
        return [], f"failed to get rates: {err_msg}"

    requests_dict = to_request_dict(codes_fiat)
    results = asyncio.get_event_loop().run_until_complete(async_get_http_results(requests_dict, api_token))

    rates = []
    for result in results:
        if result[1] != "":
            continue

        try:
            response = json.loads(result[0])
            from_code =  response['response']['base']
            for to_code in response['response']['rates']:
                rates.append({
                    "from": from_code,
                    "to": to_code,
                    "rate": response['response']['rates'][to_code],
                    "updatedAt": datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3]
                })
        except json.decoder.JSONDecodeError:
            continue

    return rates


async def async_get_http_results(requests_dict, api_token):
    loop = asyncio.get_event_loop()

    futures = [loop.run_in_executor(None, __http_get,
                                    f"https://api.currencybeacon.com/v1/latest?base={code}&symbols={','.join(requests_dict[code])}&api_key={api_token}")
               for code in requests_dict]
    return [await x for x in futures]


def __http_get(url_str):
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
        print(to_request_dict(["EUR", "KZT", "RUB", "TRY", "RSD", "CAD", "CHF", "USD"]))
        print(to_request_dict(["EUR", "KZT", "RUB", "TRY", "RSD", "CAD", "CHF"]))
        print(get_rates_fiat(["USD", "EUR", "KZT", "RUB", "TRY", "RSD", "CAD", "CHF"]))
    except KeyboardInterrupt:
        print(f"KeyboardInterrupt, exiting ...")
        quit(0)
