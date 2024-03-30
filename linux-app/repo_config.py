import json
import os


def validate_code(code):
    """returns (corr_code, type<fiat|crypto>, errMsg);
    """
    config, err_msg = _get_config()
    if err_msg != "":
        return "", "", f"failed to validate: {err_msg}"

    for x in config['supportedCrypto']:
        if x['code'].lower() == code.lower() or code.lower() in [i.lower() for i in x['synonyms']]:
            return x['code'], "crypto", ""

    for x in config['supportedFiat']:
        if x['code'].lower() == code.lower() or code.lower() in [i.lower() for i in x['synonyms']]:
            return x['code'], "fiat", ""

    return "", "", f"No fiat or crypto with code '{code}' found in supported"


def _get_config():
    configs_dir = os.getenv('RR_CONFIGS_DIR', os.path.abspath(os.getcwd()))
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
        print(validate_code("USDT"))
        print(validate_code("usdt"))
        print(validate_code("tetHer"))
        print(validate_code("sdf"))
    except KeyboardInterrupt:
        print(f"KeyboardInterrupt, exiting ...")
        quit(0)
