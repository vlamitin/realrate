import repo_config
import repo_storage

DESCRIPTION = 'removes given code from of favorite crypto/fiat'


def add_arguments(arg_parser):
    arg_parser.add_argument('--code', nargs=1, type=str, help='crypto/fiat code to clean')

    return arg_parser


def parse_args(args_dict):
    return args_dict['code'] and args_dict['code'][0] or ''


# returns (successMsg, errMsg)
def clean_favorite(code):
    corr_code, code_type, err_msg = repo_config.validate_code(code)
    if err_msg != "":
        return "", f"failed to clean favorite: {err_msg}"

    cleaned, err_msg = repo_storage.clean_favorite(corr_code, code_type)
    if err_msg != "":
        return "", f"failed to clean favorite {code_type}: {err_msg}"
    elif not cleaned:
        return f"'{corr_code}' wasn't in favorite {code_type} list", ""

    return f"Successfully cleaned '{corr_code}' from favorite {code_type} list", ""
