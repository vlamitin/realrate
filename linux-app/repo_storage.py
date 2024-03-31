from decimal import *
from datetime import datetime
import json
import os
import pathlib

import repo_config


def get_selected():
    """returns (selectedFrom, selectedTo, err_msg)
    """
    storage, err_msg = _get_storage()
    if err_msg != "":
        return "", "", err_msg

    return storage['selectedFrom'], storage['selectedTo'], ""


def get_favorites():
    """returns ([...favorite_crypto], [...favorite_fiat], err_msg)
    """
    storage, err_msg = _get_storage()
    if err_msg != "":
        return [], [], err_msg

    return storage['favoriteCrypto'], storage['favoriteFiat'], ""


def get_oldest_rate_update():
    """returns (updated_at<str>, err_msg)
    """
    storage, err_msg = _get_storage()
    if err_msg != "":
        return "", err_msg

    oldest = ""
    oldest_ts = datetime.timestamp(datetime.now())
    for rate in storage['fetchedCryptoRates'] + storage['fetchedFiatRates'] + storage['fetchedCryptoToFiatRates']:
        updated_at_ts = datetime.timestamp(datetime.strptime(rate['updatedAt'], "%Y-%m-%d %H:%M:%S"))
        if updated_at_ts < oldest_ts:
            oldest = rate['updatedAt']
            oldest_ts = updated_at_ts

    return oldest, ""


def get_rates_as_graph():
    """returns (graph_dict, err_msg), graph example:
    {
      "BTC": {"USDT": 69784.7982867},
      "USDT": {"BTC": 0.00001432976843884617181026619031, "USD": 1},
      "USDC": {"USD": 1},
      "DAI": {"USD": 1},
      "USD": {"USDT": 1, "USDC": 1, "DAI": 1, "KZT": 449.836},
      "KZT": {"USD": 0.002223032394028045713758555164, "EUR": 0.002054316118164263231956302143},
      "EUR": {"KZT": 486.78}
    }
    """
    storage, err_msg = _get_storage()
    if err_msg != "":
        return "", err_msg

    graph = {}
    for rate in storage['fetchedCryptoRates'] + storage['fetchedFiatRates'] + storage['fetchedCryptoToFiatRates']:
        if rate['from'] not in graph:
            graph[rate['from']] = {}
        if rate['to'] not in graph:
            graph[rate['to']] = {}

        graph[rate['from']][rate['to']] = rate['rate']

        if rate['from'] not in rate['to']:
            graph[rate['to']][rate['from']] = float(Decimal(1) / Decimal(rate['rate']))

    return graph, ""


def set_selected_from(code):
    """returns err_msg
    """
    storage, err_msg = _get_storage()
    if err_msg != "":
        return f"failed to set code: {err_msg}"

    storage['selectedFrom'] = code
    return _write_storage(storage)


def set_selected_to(code):
    """returns err_msg
    """
    storage, err_msg = _get_storage()
    if err_msg != "":
        return f"failed to set code: {err_msg}"

    storage['selectedTo'] = code
    return _write_storage(storage)


def upsert_rates(rates):
    """returns (updated<int>, inserted<int>, new_total<int>, err_msg)
    >>> upsert_rates([{'from': 'USD', 'to': 'KZT', 'rate': 445.87823098, 'updatedAt': '2024-03-30T23:40:01.2375'}])
    '1, 0, 5, ""'
    """
    storage, err_msg = _get_storage()
    if err_msg != "":
        return 0, 0, 0, f"failed to update rates: {err_msg}"

    # fill temp structs from rates arg
    rates_dict = {}
    codes_list = []
    for r in rates:
        if r['from'] not in rates_dict:
            rates_dict[r['from']] = {}
        rates_dict[r['from']][r['to']] = r
        codes_list.extend([r['from'], r['to']])

    # check code_type for given codes in rates arg
    results, err_msg = repo_config.validate_codes(codes_list)
    if err_msg != "":
        return 0, 0, 0, f"failed to update rates: {err_msg}"
    fiat_codes = set()
    crypto_codes = set()
    for r in results:
        if not r[2]:
            # TODO this may lead to undefined behavior, we should handle it!
            continue
        if r[1] == "fiat":
            fiat_codes.add(r[0])
        elif r[1] == "crypto":
            crypto_codes.add(r[0])

    # update rates
    updated = 0
    for storage_key in ['fetchedCryptoRates', 'fetchedFiatRates', 'fetchedCryptoToFiatRates']:
        for i in range(len(storage[storage_key])):
            fr = storage[storage_key][i]['from']
            to = storage[storage_key][i]['to']

            if fr not in rates_dict:
                continue
            if to not in rates_dict[fr]:
                continue

            storage[storage_key][i] = rates_dict[fr][to]
            del rates_dict[fr][to]
            if len(rates_dict[fr]) == 0:
                del rates_dict[fr]
            updated = updated + 1

    # insert new rates
    inserted = 0
    for fr in rates_dict:
        fr_type = "fiat" if fr in fiat_codes else "crypto"
        for to in rates_dict[fr]:
            to_type = "fiat" if to in fiat_codes else "crypto"

            if fr_type == to_type == "fiat":
                storage['fetchedFiatRates'].append(rates_dict[fr][to])
            elif fr_type == to_type == "crypto":
                storage['fetchedCryptoRates'].append(rates_dict[fr][to])
            else:
                storage['fetchedCryptoToFiatRates'].append(rates_dict[fr][to])
            inserted = inserted + 1

    err_msg = _write_storage(storage)
    if err_msg != "":
        return 0, 0, 0, f"failed to update rates: {err_msg}"

    return updated, inserted, len(storage['fetchedFiatRates']) + len(storage['fetchedCryptoRates']) + len(
        storage['fetchedCryptoToFiatRates']), ""


def _write_storage(storage):
    """returns err_msg
    """
    configs_dir = os.getenv('RR_CONFIGS_DIR', os.path.abspath(pathlib.Path(__file__).parent.resolve()))
    storage_path = os.path.join(configs_dir, "rr_storage.json")
    try:
        with open(storage_path, "w") as f:
            f.write(
                json.dumps(storage, indent=2, sort_keys=False) + "\n"
            )
            return ""
    except FileNotFoundError:
        return f"storage file not found in {storage_path}"
    except json.decoder.JSONDecodeError:
        return f"storage file {storage_path} is invalid"
    except:
        return f"something went wrong when write storage"


def add_favorite(code, code_type):
    """returns (added<bool>, err_msg)
    """
    storage, err_msg = _get_storage()
    if err_msg != "":
        return False, f"failed to add favorite: {err_msg}"

    if code_type == "fiat":
        if code in storage['favoriteFiat']:
            return False, ""
        storage['favoriteFiat'].append(code)
    elif code_type == "crypto":
        if code in storage['favoriteCrypto']:
            return False, ""
        storage['favoriteCrypto'].append(code)

    err_msg = _write_storage(storage)
    if err_msg != "":
        return False, f"failed to add favorite: {err_msg}"

    return True, ""


def clean_favorite(code, code_type):
    """returns (cleaned<bool>, err_msg)
    """
    storage, err_msg = _get_storage()
    if err_msg != "":
        return False, f"failed to clean favorite: {err_msg}"

    if code_type == "fiat":
        if code not in storage['favoriteFiat']:
            return False, ""
        storage['favoriteFiat'] = [x for x in storage['favoriteFiat'] if x != code]
    elif code_type == "crypto":
        if code not in storage['favoriteCrypto']:
            return False, ""
        storage['favoriteCrypto'] = [x for x in storage['favoriteCrypto'] if x != code]

    err_msg = _write_storage(storage)
    if err_msg != "":
        return False, f"failed to clean favorite: {err_msg}"

    return True, ""


def _get_storage():
    """returns (storage, err_msg)
    """
    configs_dir = os.getenv('RR_CONFIGS_DIR', os.path.abspath(pathlib.Path(__file__).parent.resolve()))
    storage_path = os.path.join(configs_dir, "rr_storage.json")
    try:
        with open(storage_path, "r") as f:
            storage = json.loads(f.read())
            return storage, ""
    except FileNotFoundError:
        return None, f"storage file not found in {storage_path}"
    except json.decoder.JSONDecodeError:
        return None, f"storage file {storage_path} is invalid"
    except:
        return f"something went wrong when get storage"


if __name__ == '__main__':
    try:
        print(upsert_rates([{'from': 'USD', 'to': 'KZT', 'rate': 445.87823098, 'updatedAt': '2024-03-30T23:40:01.2375'}]))
        # print(get_rates_as_graph())
    except KeyboardInterrupt:
        print(f"KeyboardInterrupt, exiting ...")
        quit(0)
