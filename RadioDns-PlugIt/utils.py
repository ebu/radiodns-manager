import math
import random

import requests

import config


def safe_cast(val, target_type, default=None):
    """
    Tries to cast a value to a specific target value. Return None or specified
     default value if casting failed.

    :param val: Value to be cast.
    :param target_type: Target type (int, float, string, etc).
    :param default: Must be of the expected type. Default value if cast failed.
    :return: Casted value if success, default value otherwise.
    """
    try:
        return target_type(val)
    except (ValueError, TypeError):
        return default


def sendImageToMockApi(image, size_prefix=""):
    """
    Standalone function allowing to send an image to any mock api server.

    :param image: the image to send. For example: {name: open(full_path, 'rb')}
    :param size_prefix: the size (in pixels) of the image. For example: "32x32".
    """
    requests.post(config.LOGO_INTERNAL_URL + ("" if size_prefix == "" else "/") + size_prefix, files=image)
