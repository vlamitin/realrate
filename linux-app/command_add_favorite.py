import repo_config
import repo_storage

DESCRIPTION = 'adds given code to list of favorite crypto/fiat'


def add_arguments(arg_parser):
    arg_parser.add_argument('--code', nargs=1, type=str, help='crypto/fiat code to add')

    return arg_parser


def parse_args(args_dict):
    return args_dict['code'] and args_dict['code'][0] or ''


def add_favorite(code):
    """returns (success_msg, err_msg)
    """
    results, err_msg = repo_config.validate_codes([code])
    if err_msg != "":
        return "", f"failed to add favorite: {err_msg}"
    corr_code, code_type, valid = results[0]
    if not valid:
        return "", f"failed to add favorite: '{code}' is not supported"

    added, err_msg = repo_storage.add_favorite(corr_code, code_type)
    if err_msg != "":
        return "", f"failed to add favorite {code_type}: {err_msg}"
    elif not added:
        return f"'{corr_code}' was already in favorite {code_type} list", ""

    return f"Successfully added '{corr_code}' to favorite {code_type} list", ""
