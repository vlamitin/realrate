import json
import os
import repo_config


# returns (selectedFrom, selectedTo, errMsg)
def get_selected():
    storage, err_msg = _get_storage()
    if err_msg != "":
        return "", "", err_msg

    return storage['selectedFrom'], storage['selectedTo'], ""


# returns errMsg
def set_selected_from(code):
    storage, err_msg = _get_storage()
    if err_msg != "":
        return f"failed to set code: {err_msg}"

    configs_dir = os.getenv('RR_CONFIGS_DIR', os.path.abspath(os.getcwd()))
    storage_path = os.path.join(configs_dir, "rr_storage.json")
    try:
        with open(storage_path, "w") as f:
            storage['selectedFrom'] = code
            f.write(
                json.dumps(storage, indent=2, sort_keys=False) + "\n"
            )
            return ""
    except FileNotFoundError:
        return f"storage file not found in {storage_path}"
    except json.decoder.JSONDecodeError:
        return f"storage file {storage_path} is invalid"
    # except:
    #     return f"something went wrong when set selected from"


# returns errMsg
def set_selected_to(code):
    storage, err_msg = _get_storage()
    if err_msg != "":
        return f"failed to set code: {err_msg}"

    configs_dir = os.getenv('RR_CONFIGS_DIR', os.path.abspath(os.getcwd()))
    storage_path = os.path.join(configs_dir, "rr_storage.json")
    try:
        with open(storage_path, "w") as f:
            storage['selectedTo'] = code
            f.write(
                json.dumps(storage, indent=2, sort_keys=False) + "\n"
            )
            return ""
    except FileNotFoundError:
        return f"storage file not found in {storage_path}"
    except json.decoder.JSONDecodeError:
        return f"storage file {storage_path} is invalid"
    except:
        return f"something went wrong when set selected from"


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
