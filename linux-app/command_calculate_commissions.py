import repo_config
import repo_storage
import command_clean_input

DESCRIPTION = 'shows comparison of selected price with fair market price (selected price should be the number, and "from" and "to" should be previously set)'


def add_arguments(arg_parser):
    arg_parser.add_argument('--selected_price', nargs=1, type=str,
                            help="number, or string that we will try to convert to number")

    return arg_parser


def parse_args(args_dict):
    return args_dict['selected_price'] and args_dict['selected_price'][0] or ''


def calculate_comissions(selected_price):
    """returns (successMsg, errMsg)
    """
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


def get_shortest_path(graph, code1, code2):
    """returns path, for example ["USD", "BTC", "KZT"]
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


def calculate_market_rate(graph, code_from, code_to):
    """ return (rate<number>, errMsg)
    """
    codes_path = get_shortest_path(graph, code_from, code_to)
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
        test_graph = {
            "BTC": {"USDT": 69784.7982867},
            "USDT": {"BTC": 0.00001432976843884617181026619031, "USD": 1},
            "USDC": {"USD": 1},
            "DAI": {"USD": 1},
            "USD": {"USDT": 1, "USDC": 1, "DAI": 1, "KZT": 449.836},
            "KZT": {"USD": 0.002223032394028045713758555164, "EUR": 0.002054316118164263231956302143},
            "EUR": {"KZT": 486.78}
        }
        print(get_shortest_path(test_graph, "EUR", "RUB"))
        print(calculate_market_rate(test_graph, "EUR", "RUB"))

        print(get_shortest_path(test_graph, "EUR", "EUR"))
        print(calculate_market_rate(test_graph, "EUR", "EUR"))

        print(get_shortest_path(test_graph, "DAI", "KZT"))
        print(calculate_market_rate(test_graph, "DAI", "KZT"))

        print(get_shortest_path(test_graph, "BTC", "KZT"))
        print(calculate_market_rate(test_graph, "BTC", "KZT"))

        print(test_graph['BTC']['USDT'] * test_graph['USDT']['USD'] * test_graph['USD']['KZT'])
    except KeyboardInterrupt:
        print(f"KeyboardInterrupt, exiting ...")
        quit(0)
