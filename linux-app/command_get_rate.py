import repo_config
import repo_storage
import command_force_update_rates

DESCRIPTION = 'returns just number of from/to rate'


def add_arguments(arg_parser):
    arg_parser.add_argument('--from', nargs=1, type=str, help='crypto/fiat code from')
    arg_parser.add_argument('--to', nargs=1, type=str, help='crypto/fiat code to')

    return arg_parser


def parse_args(args_dict):
    return args_dict['from'] and args_dict['from'][0] or '', args_dict['to'] and args_dict['to'][0] or ''


def get_rate(from_code, to_code):
    """returns (success_msg, err_msg)
    """
    results, err_msg = repo_config.validate_codes([from_code, to_code])
    if err_msg != "":
        return "", f"failed to get rate: {err_msg}"
    corr_from_code, _, from_valid = results[0]
    corr_to_code, _, to_valid = results[1]
    if not from_valid or not to_valid:
        return "", f"failed to get rate: '{from_code}' or '{to_code}' is not supported"

    _, _ = command_force_update_rates.update_outdated_rates()

    graph, err_msg = repo_storage.get_rates_as_graph()
    if err_msg != "":
        return "", f"failed to get rate: {err_msg}"

    market_rate, err_msg = calculate_market_rate(graph, corr_from_code, corr_to_code)
    if err_msg != "":
        return "", f"failed to get rate: {err_msg}"

    return f"{market_rate}", ""


# TODO duplicate
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


# TODO duplicate
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


if __name__ == '__main__':
    try:
        print(get_rate("BTC", "USD"))
    except KeyboardInterrupt:
        print(f"KeyboardInterrupt, exiting ...")
        quit(0)
