import repo_config
import repo_storage

DESCRIPTION = 'sets given code as "from"'


def add_arguments(arg_parser):
    arg_parser.add_argument('--code', nargs=1, type=str, help='crypto/fiat code to set as')

    return arg_parser


def parse_args(args_dict):
    return args_dict['code'] and args_dict['code'][0] or ''


def set_from(code):
    """returns (successMsg, err_msg)
    """
    corr_code, _, err_msg = repo_config.validate_code(code)
    if err_msg != "":
        return "", f"failed to set 'from': {err_msg}"

    err_msg = repo_storage.set_selected_from(corr_code)
    if err_msg != "":
        return "", f"failed to set 'from': {err_msg}"

    return f"Successfully set {corr_code} as 'from'", ""
