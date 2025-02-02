from time import sleep

from includes.config import *
from util.connect import resize_volume_linnode, resize_volume_digital_ocean
from util.volume_utils import check_volume_size, resize_volume_linux
from util.send_alerts import send_success_alerts, send_error_alerts, send_to_vstats


def run(provider_info: tuple) -> None:
    func, provider = provider_info
    while True:
        resize_msg = ""
        try:
            # get VOLUME size %
            org_volume_sizes = check_volume_size(VOLUME_NAME)
            volume_size_remaining = 100 - org_volume_sizes["percent"]
            log.info(f"VOLUME Size  ::  {volume_size_remaining}% Remaining..")

            # Check if it is < BELOW_THIS_PERCENT_TO_RESIZE
            if volume_size_remaining <= BELOW_THIS_PERCENT_TO_RESIZE:
                log.info(
                    f"VOLUME Size [ {volume_size_remaining}% ] is <= {BELOW_THIS_PERCENT_TO_RESIZE}%.. Increasing size on {provider} volume {VOLUME_NAME}"
                )
                # resize VOLUME on Digital Ocean
                full, flat, resize_msg = func(
                    INCREASE_BY_PERCENTAGE, VOLUME_NAME, TOKEN, ENDPOINT
                )
                if flat.get("status") in ("done", "resizing"):
                    log.info(f"VOLUME Size increased.. Increasing size on System")
                    # resize on Linux
                    res, msg = resize_volume_linux(VOLUME_NAME, org_volume_sizes)
                    if res:
                        log.info("VOLUME Resize Successful.. ")
                        # send email success
                        send_success_alerts(msg, VOLUME_NAME, resize_msg)
                        log.info(f"sleeping for {HOURS} Hour(s)..")

                    else:
                        log.error(f"Failed to resize volume on System..")
                        send_error_alerts(msg, VOLUME_NAME, resize_msg)
                else:
                    log.error(
                        f"Failed to resize volume on {provider}\n{full}\n{flat}.."
                    )
                    send_error_alerts(full, VOLUME_NAME, resize_msg)

            else:
                log.info(f"VOLUME Size is healthy, sleeping for {HOURS} Hour(s)..")
        except Exception as e:
            send_error_alerts(e, VOLUME_NAME, resize_msg)
            log.error(e)
            log.error(
                f"Error email sent, sleeping for {HOURS} Hour(s).. Please fix me!"
            )
        sleep(DELAY)


providers = {
    "DO": (resize_volume_digital_ocean, "Digital Ocean"),
    "LN": (resize_volume_linnode, "LinNode"),
}

run(providers[PROVIDER])


# For testing messages..
# send_to_vstats(f'Beans  ( volume-sfo3-11 )', 'On toast with Cheese', 'success')
