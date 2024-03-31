from datetime import datetime
import json
import os
import pathlib


def get_cb_api_token():
    """returns (api_key<str>, err_msg);
    """
    config, err_msg = _get_config()
    if err_msg != "":
        return "", err_msg
    if config['apiTokenCurrencybeacon'] == "":
        return "", "token is empty!"

    return config['apiTokenCurrencybeacon'], ""


def is_rate_outdated(updated_at):
    """returns (bool<true if outdated, false if fresh>, err_msg);
    """
    config, err_msg = _get_config()
    if err_msg != "":
        return False, err_msg

    updated_at_ts = datetime.timestamp(datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S"))
    now_ts = datetime.timestamp(datetime.now())

    if now_ts - updated_at_ts > config['ratesMaxLifeMinutes'] * 60:
        return True, ""
    return False, ""


def validate_codes(codes):
    """returns ([(corr_code, type<fiat|crypto>, is_valid<bool>)], err_msg);
    """
    if len(codes) == 0:
        return [], f"empty codes to validate"
    config, err_msg = _get_config()
    if err_msg != "":
        return [], f"failed to validate: {err_msg}"

    results = []
    for code in codes:
        for x in config['supportedCrypto']:
            if x['code'].lower() == code.lower() or code.lower() in [i.lower() for i in x['synonyms']]:
                results.append((x['code'], "crypto", True))
                break
        else:
            for x in config['supportedFiat']:
                if x['code'].lower() == code.lower() or code.lower() in [i.lower() for i in x['synonyms']]:
                    results.append((x['code'], "fiat", True))
                    break
            else:
                results.append(("", "", False))

    return results, ""


def _get_config():
    configs_dir = os.getenv('RR_CONFIGS_DIR', os.path.abspath(pathlib.Path(__file__).parent.resolve()))
    config_path = os.path.join(configs_dir, "rr_config.json")
    try:
        with open(config_path, "r") as f:
            config = json.loads(f.read())
            return config, ""
    except FileNotFoundError:
        return None, f"config file not found in {config_path}"
    except json.decoder.JSONDecodeError:
        return None, f"config file {config_path} is invalid"
    except:
        return None, f"something went wrong when get config"


if __name__ == '__main__':
    try:
        print(validate_codes(["USDT"]))
        print(validate_codes(["usdt"]))
        print(validate_codes(["tetHer"]))
        print(validate_codes(["sdf"]))
        print(validate_codes(["tenge"]))
        print(validate_codes(["USDT", "USDC", "DAI", "BTC", "EUR", "USD", "KZT"]))
        print(is_rate_outdated("2024-03-27 16:17:23"))
        print(is_rate_outdated("2024-03-31 00:01:23"))
        print(is_rate_outdated("2024-03-30 23:45:23"))
    except KeyboardInterrupt:
        print(f"KeyboardInterrupt, exiting ...")
        quit(0)
