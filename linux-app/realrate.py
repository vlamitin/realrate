import argparse

import command_set_from
import command_set_to
import command_add_favorite
import command_clean_favorite
import command_calculate_commissions
import command_clean_input


def run_scenario():
    """returns (result<str>, err_msg)
    """
    arg_parser = argparse.ArgumentParser(prog="realrate", description="Type realrate {command} -h for each command help")
    subparsers = arg_parser.add_subparsers(title="commands", dest="command")

    command_set_from.add_arguments(subparsers.add_parser('set_from', help=command_set_from.DESCRIPTION))
    command_set_to.add_arguments(subparsers.add_parser('set_to', help=command_set_to.DESCRIPTION))
    command_add_favorite.add_arguments(subparsers.add_parser('add_favorite', help=command_add_favorite.DESCRIPTION))
    command_clean_favorite.add_arguments(subparsers.add_parser('clean_favorite', help=command_clean_favorite.DESCRIPTION))
    command_calculate_commissions.add_arguments(subparsers.add_parser('calculate_comissions', help=command_calculate_commissions.DESCRIPTION))
    command_clean_input.add_arguments(subparsers.add_parser('clean_input', help=command_clean_input.DESCRIPTION))

    # get_rates - shows rate for 1 unit, depending on what is selected
    #   if crypto is selected - shows its rates in favorite fiats; if fiat is selected - shows favorite crypto rates
    # calculate_commissions - shows comparison of selected price with fair market price
    #   selected price should be the number, and "from" and "to" should be previously set

    args = arg_parser.parse_args()
    args_dict = vars(args)

    if args_dict['command'] == 'set_from':
        return command_set_from.set_from(command_set_from.parse_args(args_dict))
    elif args_dict['command'] == 'set_to':
        return command_set_to.set_to(command_set_to.parse_args(args_dict))
    elif args_dict['command'] == 'add_favorite':
        return command_add_favorite.add_favorite(command_add_favorite.parse_args(args_dict))
    elif args_dict['command'] == 'clean_favorite':
        return command_clean_favorite.clean_favorite(command_clean_favorite.parse_args(args_dict))
    elif args_dict['command'] == 'calculate_comissions':
        return command_calculate_commissions.calculate_comissions(command_calculate_commissions.parse_args(args_dict))
    elif args_dict['command'] == 'clean_input':
        return command_clean_input.clean_input(command_clean_input.parse_args(args_dict))
    # elif args_dict['command'] == 'merge_prs_local':
    #     arguments_dict = merge_prs_local.parse_args(args_dict)
    #     merge_prs_local.run_scenario(arguments_dict['merge_branch_name'], arguments_dict['base_branch_name'])
    # elif args_dict['command'] == 'print_jira_tree':
    #     arguments_dict = print_jira_tree.parse_args(args_dict)
    #     print_jira_tree.run_scenario(arguments_dict['task_key'])
    # elif args_dict['command'] == 'update_prs':
    #     arguments_dict = update_prs.parse_args(args_dict)
    #     update_prs.run_scenario(arguments_dict['base_branch'])
    # elif args_dict['command'] == 'cherry':
    #     arguments_dict = cherry.parse_args(args_dict)
    #     cherry.run_scenario(arguments_dict['commits_count_or_jira_key'])
    # elif args_dict['command'] == 'worklog':
    #     arguments_dict = worklog.parse_args(args_dict)
    #     worklog.run_scenario(
    #         arguments_dict['jira_key'],
    #         arguments_dict['jira_period_pieces'],
    #     )
    else:
        arg_parser.print_usage()
        return "", ""



if __name__ == '__main__':
    try:
        result, err_msg = run_scenario()
        if err_msg != "":
            print(err_msg)
            quit(1)
        elif result != "":
            print(result)
    except KeyboardInterrupt:
        print(f"KeyboardInterrupt, exiting ...")
        quit(0)
