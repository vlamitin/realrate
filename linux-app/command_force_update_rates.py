import repo_config
import repo_storage
import api_currencybeacon
import api_rate_sx

DESCRIPTION = 'updates saved rates even if they are not outdated according to config'


def update_outdated_rates():
    """returns (success_msg, err_msg)
    """
    oldest_rate_update, err_msg = repo_storage.get_oldest_rate_update()
    if err_msg != "":
        return "", f"failed to update outdated rates: {err_msg}"

    is_outdated, err_msg = repo_config.is_rate_outdated(oldest_rate_update)
    if err_msg != "":
        return "", f"failed to update outdated rates: {err_msg}"

    if is_outdated:
        return force_update_rates()

    return f"Latest update was at {oldest_rate_update}, no need to update yet", ""


def force_update_rates():
    """returns (success_msg, err_msg)
    """
    codes_crypto, codes_fiat, err_msg = repo_storage.get_favorites()
    if err_msg != "":
        return "", f"failed to update rates: {err_msg}"

    fiat_rates, err_msg = api_currencybeacon.get_rates_fiat(codes_fiat)
    if err_msg != "":
        return "", f"failed to update rates: {err_msg}"

    crypto_rates = api_rate_sx.get_rates(codes_crypto)

    updated, inserted, total, err_msg = repo_storage.upsert_rates(crypto_rates + fiat_rates)
    if err_msg != "":
        return "", f"failed to update rates: {err_msg}"

    return f"{updated} updated, {inserted} inserted, {total} new total, {len(fiat_rates)} fiat fetched, {len(crypto_rates)} crypto fetched", ""


if __name__ == '__main__':
    try:
        print(force_update_rates())
    except KeyboardInterrupt:
        print(f"KeyboardInterrupt, exiting ...")
        quit(0)