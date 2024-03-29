import json
import os
import repo_config


# returns (selectedFrom, selectedTo, errMsg)
def get_selected():
    storage, err_msg = _get_storage()
    if err_msg != "":
        return "", "", err_msg

    return storage['selectedFrom'], storage['selectedTo'], ""



# returns (fetchedCryptoRates, fetchedFiatRates, fetchedCryptoToFiatRates, errMsg)
def get_rates():
    storage, err_msg = _get_storage()
    if err_msg != "":
        return None, None, None, err_msg

    return storage['fetchedCryptoRates'], storage['fetchedFiatRates'],  storage['fetchedCryptoToFiatRates'], ""


# returns errMsg
def set_selected_from(code):
    storage, err_msg = _get_storage()
    if err_msg != "":
        return f"failed to set code: {err_msg}"

    storage['selectedFrom'] = code
    return _write_storage(storage)


# returns errMsg
def set_selected_to(code):
    storage, err_msg = _get_storage()
    if err_msg != "":
        return f"failed to set code: {err_msg}"

    storage['selectedTo'] = code
    return _write_storage(storage)


# return errMsg
def _write_storage(storage):
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


# returns (added<bool>, errMsg)
def add_favorite(code, code_type):
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


# returns (cleaned<bool>, errMsg)
def clean_favorite(code, code_type):
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


# returns (storage, errMsg)
def _get_storage():
    configs_dir = os.getenv('RR_CONFIGS_DIR', os.path.abspath(os.getcwd()))
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
        print(set_selected_from("euro"))
        # print(set_selected_to("euro"))
    except KeyboardInterrupt:
        print(f"KeyboardInterrupt, exiting ...")
        quit(0)
