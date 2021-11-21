import requests
import json

try:
    from util.tools import flatten
    from includes.config import *
except ModuleNotFoundError:
    from tools import flatten
    from config import *


def connect_to_api(
    token: str,
    api: str,
    endpoint: str,
    call: requests = requests.get,
    j: dict = {},
    key: str = "",
    rtn_data: tuple = (),
) -> dict:

    rtn = {}

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        r = call(api + endpoint, json=j, headers=headers)
        data = r.json()
    except json.decoder.JSONDecodeError:
        data = r.text
    if data.get("errors"):
        return data, data

    rtn = data

    if rtn_data:
        try:
            rtn = {k: v for k, v in data[key].items() if k in rtn_data}
        except (KeyError, AttributeError) as e:
            log.info(f"problem with response key, see error {e}")
            try:
                rtn = {k: v for k, v in data.items() if k in rtn_data}
            except:
                pass

    return rtn, flatten(rtn)


def resize_volume_digital_ocean(
    percentage_increase: int, volume_name: str, token: str, endpoint: str
) -> connect_to_api:

    get_volume_data, _ = connect_to_api(
        token, DO_API, endpoint + f"?name={volume_name}"
    )
    volumes = get_volume_data[0]["volumes"]
    volume = flatten([x for x in volumes if x["name"] == volume_name][0])
    size = volume["size_gigabytes"]
    volume_id = volume["id"]
    region = volume["slug"]
    new_size = size + round((size / 100 * int(percentage_increase)), None)

    j = {"type": "resize", "size_gigabytes": new_size, "region": region}  # slug
    e = f"{endpoint}/{volume_id}/actions"

    log.info(f"Resizing Volume {volume_name} from {size} GB -> {new_size} GB")

    return connect_to_api(
        token,
        DO_API,
        e,
        j=j,
        call=requests.post,
        key="action",
        rtn_data=("type", "id", "status"),
    )


def resize_volume_linnode(
    percentage_increase: int, volume_name: str, token: str, endpoint: str
) -> connect_to_api:

    get_volume_data, _ = connect_to_api(token, LN_API, endpoint)
    volumes = get_volume_data["data"]
    volume = flatten([x for x in volumes if x["label"] == volume_name][0])
    size = int(volume["size"])
    volume_id = volume["id"]
    new_size = size + round((size / 100 * int(percentage_increase)), None)

    j = {"size": new_size}  # slug
    e = f"{endpoint}/{volume_id}/resize"

    log.info(f"Resizing Volume {volume_name} from {size} GB -> {new_size} GB")

    return connect_to_api(
        token, LN_API, e, j=j, call=requests.post, rtn_data=("size", "id", "status"),
    )


if __name__ == "__main__":
    # full, flat = connect_to_api(TOKEN, LN_API, ENDPOINT, requests.get)

    # print(full)
    print(SEND_EMAIL)
    if not SEND_EMAIL:
        print(INCREASE_BY_PERCENTAGE, VOLUME_NAME, TOKEN, ENDPOINT)
        full, flat = resize_volume_linnode(
            INCREASE_BY_PERCENTAGE, VOLUME_NAME, TOKEN, ENDPOINT
        )

        print(flat.get("status"))
        print(full)
