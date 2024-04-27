import repo_storage

DESCRIPTION = 'switches "from" and "to" selected codes'


def switch_selected():
    """returns (success_msg, err_msg)
    """
    err_msg = repo_storage.switch_selected()
    if err_msg != "":
        return "", f"failed to switch selected"

    selected_from, selected_to, _ = repo_storage.get_selected()

    return f"Successfully switched selected. Current pair is '{selected_from}' -> '{selected_to}'", ""


if __name__ == '__main__':
    try:
        print(switch_selected())
    except KeyboardInterrupt:
        print(f"KeyboardInterrupt, exiting ...")
        quit(0)
