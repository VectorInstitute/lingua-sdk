"""
TODOS:
    1. eventually we need to seperate this out to client and server utils
"""
import logging
import json
import requests
import pickle
import codecs

logger = logging.getLogger(__name__)


def decode_str(obj_in_str):
    return pickle.loads(codecs.decode(obj_in_str.encode("utf-8"), "base64"))


def check_response(resp):
    if not resp.ok:
        if resp.status_code == 422:
            raise ValueError(
                "Request to {} not sucessful, Error Code: {}, please check your auth key".format(
                    resp.url, resp.status_code
                )
            )
        elif resp.status_code == 400:
            raise ValueError(
                "Request to {} not sucessful, Error Code: {}, please check your request body".format(
                    resp.url, resp.status_code
                )
            )
        raise ValueError(
            "Request to {} not sucessful, Error Code: {}".format(
                resp.url, resp.status_code
            )
        )
    logger.debug("addr %s response code %s", resp.url, resp.status_code)


def get(addr, auth_key=None, headers={}):

    if auth_key:
        headers["Authorization"] = f"Bearer {auth_key}"

    resp = requests.get(addr, headers=headers)
    check_response(resp)

    return resp.json()


def post(addr, body, auth_key=None, headers={}):

    if auth_key:
        headers["Authorization"] = f"Bearer {auth_key}"

    resp = requests.post(addr, json=body, headers=headers)
    check_response(resp)

    return resp.json()
