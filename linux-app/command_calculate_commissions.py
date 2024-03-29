import repo_config
import repo_storage
import command_clean_input

DESCRIPTION = 'shows comparison of selected price with fair market price (selected price should be the number, and "from" and "to" should be previously set)'


def add_arguments(arg_parser):
    arg_parser.add_argument('--selected_price', nargs=1, type=str, help="number, or string that we will try to convert to number")

    return arg_parser


def parse_args(args_dict):
    return args_dict['selected_price'] and args_dict['selected_price'][0] or ''


# returns (successMsg, errMsg)
def calculate_comissions(selected_price):
    num, err_msg = command_clean_input.to_num(selected_price)
    if err_msg != "":
        return "", f"cannot convert '{selected_price}' to numeric: {err_msg}"

    sel_from, sel_to, err_msg = repo_storage.get_selected()
    if err_msg != "":
        return "", f"failed to calculate comissions:{err_msg}"
    if sel_from == "":
        return "", "Nothing is selected as 'from'"
    if sel_to != "":
        return "", "Nothing is selected as 'to'"

    _, from_type, _ = repo_config.validate_code(sel_from)
    _, to_type, _ = repo_config.validate_code(sel_to)

    crypto_rates, fiat_rates, crypto_to_fiat_rates, err_msg = repo_storage.get_rates()
    if err_msg != "":
        return "", f"failed to calculate comissions:{err_msg}"

    if from_type == "crypto" and to_type == "fiat":
        ...

    return f"", ""
