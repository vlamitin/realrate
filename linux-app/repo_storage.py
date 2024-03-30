import json
import os
import pathlib

import repo_config


def get_selected():
    """returns (selectedFrom, selectedTo, errMsg)
    """
    storage, err_msg = _get_storage()
    if err_msg != "":
        return "", "", err_msg

    return storage['selectedFrom'], storage['selectedTo'], ""


def get_rates():
    """returns (fetchedCryptoRates, fetchedFiatRates, fetchedCryptoToFiatRates, errMsg)
    """
    storage, err_msg = _get_storage()
    if err_msg != "":
        return None, None, None, err_msg

    return storage['fetchedCryptoRates'], storage['fetchedFiatRates'], storage['fetchedCryptoToFiatRates'], ""


def get_rates_as_graph():
    """returns (graph_dict, errMsg), graph example:
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
    return {
        "BTC": {"USDT": 69784.7982867},
        "USDT": {"BTC": 0.00001432976843884617181026619031, "USD": 1},
        "USDC": {"USD": 1},
        "DAI": {"USD": 1},
        "USD": {"USDT": 1, "USDC": 1, "DAI": 1, "KZT": 449.836},
        "KZT": {"USD": 0.002223032394028045713758555164, "EUR": 0.002054316118164263231956302143},
        "EUR": {"KZT": 486.78}
    }, ""


def set_selected_from(code):
    """returns errMsg
    """
    storage, err_msg = _get_storage()
    if err_msg != "":
        return f"failed to set code: {err_msg}"

    storage['selectedFrom'] = code
    return _write_storage(storage)


def set_selected_to(code):
    """returns errMsg
    """
    storage, err_msg = _get_storage()
    if err_msg != "":
        return f"failed to set code: {err_msg}"

    storage['selectedTo'] = code
    return _write_storage(storage)


def _write_storage(storage):
    """returns errMsg
    """
    configs_dir = os.getenv('RR_CONFIGS_DIR', os.path.abspath(os.getcwd()))
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
    """returns (added<bool>, errMsg)
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
    """returns (cleaned<bool>, errMsg)
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
    """returns (storage, errMsg)
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
        print(set_selected_to("EUR"))
    except KeyboardInterrupt:
        print(f"KeyboardInterrupt, exiting ...")
        quit(0)
