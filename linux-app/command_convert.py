from decimal import *
import repo_config
import repo_storage
import command_clean_input
import command_force_update_rates

DESCRIPTION = 'shows what the selected amount of selected "from" currency is worth in selected "to" currency'


# TODO get use of decimal.Decimal in all calculations with rates

def add_arguments(arg_parser):
    arg_parser.add_argument('--selected_amount', nargs=1, type=str,
                            help="number, or string that we will try to convert to number")

    return arg_parser


def parse_args(args_dict):
    return args_dict['selected_amount'] and args_dict['selected_amount'][0] or ''


def convert(selected_amount):
    """returns (success_msg, err_msg)
    """
    selected_amount_num, err_msg = command_clean_input.to_num(selected_amount)
    if err_msg != "":
        return "", f"cannot convert '{selected_amount}' to numeric: {err_msg}"

    sel_from, sel_to, err_msg = repo_storage.get_selected()
    if err_msg != "":
        return "", f"failed to convert: {err_msg}"
    if sel_from == "":
        return "", "Nothing is selected as 'from'"
    if sel_to == "":
        return "", "Nothing is selected as 'to'"

    _, _ = command_force_update_rates.update_outdated_rates()

    graph, err_msg = repo_storage.get_rates_as_graph()
    if err_msg != "":
        return "", f"failed to calculate comissions: {err_msg}"

    market_rate, err_msg = calculate_market_rate(graph, sel_from, sel_to)
    if err_msg != "":
        return "", f"failed to calculate comissions: {err_msg}"

    result = selected_amount_num * market_rate

    return f"Market rate: 1 {sel_from} = {__fmt(market_rate)} {sel_to}. So, {__fmt(selected_amount_num)} {sel_from} = ~{__fmt(result)} {sel_to}", ""


def _get_shortest_path(graph, code1, code2):
    """returns path, for example ["USD", "BTC", "KZT"]
    or [] (when no connections for 2 codes in graph)
    or ["USD"] (when code1 and code2 are "USD")
    """
    path_list = [[code1]]
    path_index = 0
    # To keep track of previously visited nodes
    previous_nodes = {code1}
    if code1 == code2:
        return path_list[0]

    while path_index < len(path_list):
        current_path = path_list[path_index]
        last_node = current_path[-1]
        next_nodes = graph[last_node]
        # Search goal node
        if code2 in next_nodes:
            current_path.append(code2)
            return current_path
        # Add new paths
        for next_node in next_nodes:
            if not next_node in previous_nodes:
                new_path = current_path[:]
                new_path.append(next_node)
                path_list.append(new_path)
                # To avoid backtracking
                previous_nodes.add(next_node)
        # Continue to next path in list
        path_index += 1
    # No path is found
    return []


def __fmt(value):
    decimal_value = Decimal(value)
    if abs(decimal_value) < 0.01:
        return __moneyfmt(abs(value), places=12)
    elif abs(decimal_value) < 1:
        return __moneyfmt(abs(value), places=4)
    elif abs(decimal_value) < 3:
        return __moneyfmt(abs(value), places=3)
    return __moneyfmt(abs(value), places=2)


def __moneyfmt(value, places=2, curr='', sep=' ', dp='.',
               pos='', neg='-', trail_neg=''):
    """Convert Decimal to money formatted string.

    places:  required number of places after the decimal point
    curr:    optional currency symbol before the sign (may be blank)
    sep:     optional grouping separator (comma, period, space, or blank)
    dp:      decimal point indicator (comma or period)
             only specify as blank when places is zero
    pos:     optional sign for positive numbers: '+', space or blank
    neg:     optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator:  '-', ')', space or blank

    >>> d = '-1234567.8901'
    >>> __moneyfmt(d, curr='$')
    '-$1,234,567.89'
    >>> __moneyfmt(d, places=0, sep='.', dp='', neg='', trailneg='-')
    '1.234.568-'
    >>> __moneyfmt(d, curr='$', neg='(', trailneg=')')
    '($1,234,567.89)'
    >>> __moneyfmt(123456789, sep=' ')
    '123 456 789.00'
    >>> __moneyfmt(Decimal('-0.02'), neg='<', trailneg='>')
    '<0.02>'
    """

    decimal_value = Decimal(value)
    q = Decimal(10) ** -places  # 2 places --> '0.01'
    sign, digits, exp = decimal_value.quantize(q).as_tuple()
    result = []
    digits = list(map(str, digits))
    build, nxt = result.append, digits.pop
    if sign:
        build(trail_neg)
    for i in range(places):
        build(nxt() if digits else '0')
    if places:
        build(dp)
    if not digits:
        build('0')
    i = 0
    while digits:
        build(nxt())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(curr)
    build(neg if sign else pos)
    return ''.join(reversed(result))


def calculate_market_rate(graph, code_from, code_to):
    """ return (rate<number>, err_msg)
    """
    codes_path = _get_shortest_path(graph, code_from, code_to)
    if len(codes_path) == 0:
        return 0, f"no paths found to calculate rate for pair '{code_from}' -> '{code_to}'"

    result = 1
    for i in range(len(codes_path)):
        if i == 0:
            continue
        result = result * graph[codes_path[i - 1]][codes_path[i]]

    return result, ""


if __name__ == '__main__':
    try:
        # test_graph = {
        #     "BTC": {"USDT": 69784.7982867},
        #     "USDT": {"BTC": 0.00001432976843884617181026619031, "USD": 1},
        #     "USDC": {"USD": 1},
        #     "DAI": {"USD": 1},
        #     "USD": {"USDT": 1, "USDC": 1, "DAI": 1, "KZT": 449.836},
        #     "KZT": {"USD": 0.002223032394028045713758555164, "EUR": 0.002054316118164263231956302143},
        #     "EUR": {"KZT": 486.78}
        # }
        # print(_get_shortest_path(test_graph, "EUR", "RUB"))
        # print(calculate_market_rate(test_graph, "EUR", "RUB"))
        #
        # print(_get_shortest_path(test_graph, "EUR", "EUR"))
        # print(calculate_market_rate(test_graph, "EUR", "EUR"))
        #
        # print(_get_shortest_path(test_graph, "DAI", "KZT"))
        # print(calculate_market_rate(test_graph, "DAI", "KZT"))
        #
        # print(_get_shortest_path(test_graph, "BTC", "KZT"))
        # print(calculate_market_rate(test_graph, "BTC", "KZT"))
        #
        # print(test_graph['BTC']['USDT'] * test_graph['USDT']['USD'] * test_graph['USD']['KZT'])
        print(convert("65000.1234"))
        print(convert("1234123165000.1234"))
        print(convert("64000.1234"))
        print(convert("0.51234"))
    except KeyboardInterrupt:
        print(f"KeyboardInterrupt, exiting ...")
        quit(0)
