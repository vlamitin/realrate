import repo_config
import repo_storage

DESCRIPTION = 'sets given code as "to"'


def add_arguments(arg_parser):
    arg_parser.add_argument('--code', nargs=1, type=str, help='crypto/fiat code to set as')

    return arg_parser


def parse_args(args_dict):
    return args_dict['code'] and args_dict['code'][0] or ''


# returns errMsg
def set_to(code):
    return repo_storage.set_selected_to(code)
