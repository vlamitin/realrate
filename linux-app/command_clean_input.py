import re

DESCRIPTION = 'tries to convert given string to number or fiat/crypto code'


def add_arguments(arg_parser):
    arg_parser.add_argument('--dirty', nargs=1, type=str, help="input string")

    return arg_parser


def parse_args(args_dict):
    return args_dict['dirty'] and args_dict['dirty'][0] or ''


def clean_input(dirty):
    """returns (success_msg, err_msg)
    """
    num_float, err_msg = _try_float(dirty)
    if err_msg == "":
        return num_float, ""

    num_int, err_msg = _try_int(dirty)
    if err_msg == "":
        return num_int, ""

    str_word, err_msg = _try_first_word(dirty)
    if err_msg == "":
        return str_word, ""

    return f"", "failed to convert"


def to_num(dirty):
    """returns (num, err_msg)
    """
    num_float, err_msg = _try_float(dirty)
    if err_msg == "":
        return float(num_float), ""

    num_int, err_msg = _try_int(dirty)
    if err_msg == "":
        return int(num_int), ""

    return 0, "failed to convert"


def _try_float(dirty):
    """returns (int, err_msg)
    """
    to_clean_num_format = (re.sub(r'^-?0,', '0.', dirty)
                           .replace(" ", "")
                           .replace(",", ""))
    match = re.search("^-?\d+\.\d+", to_clean_num_format)
    if match is None:
        return 0, "failed to convert to float"
    return match.group(), ""


def _try_int(dirty):
    """returns (int, err_msg)
    """
    to_clean_num_format = dirty.replace(" ", "").replace(",", "")
    match = re.search("^-?\d+", to_clean_num_format)
    if match is None:
        return 0, "failed to convert to int"
    return match.group(), ""


def _try_first_word(dirty):
    """returns (int, err_msg)
    """
    to_clean_words_format = re.sub(r"[-+=.,:;!@#%^&*()]", " ", dirty)
    to_clean_words_format = to_clean_words_format.replace("  ", " ")
    to_clean_words_format = to_clean_words_format.replace("  ", " ")
    splited = to_clean_words_format.split(" ")
    if len(splited) == 0:
        return "", "failed to convert to first word"
    return splited[0][0:25], ""


if __name__ == '__main__':
    try:
        print(clean_input("0,9392"))
        print(clean_input("0,939.2"))
        print(clean_input("3,307"))
        print(clean_input("3,307.47"))
        print(clean_input("exiting"))
        print(clean_input("123,123,123asdf"))
        print(clean_input("-123 123 123asdf"))
        print(clean_input("-123 123 123.124134123asdf"))
        print(clean_input("-0.123123123.124134123asdf"))
        print(clean_input("-0.123123123124134123asdf"))
        print(clean_input("bitcoin was 13% more than"))
        print(clean_input("usdf;asdf*asdf$asd"))
        print(clean_input("usdf   asdf**asdf$asd"))
    except KeyboardInterrupt:
        print(f"KeyboardInterrupt, exiting ...")
        quit(0)
