import requests

import config


def send_image_to_mock_api(image, size_prefix=""):
    """
    Standalone function allowing to send an image to any mock api server.

    :param image: the image to send. For example: {name: open(full_path, 'rb')}
    :param size_prefix: the size (in pixels) of the image. For example: "32x32".
    """
    requests.post(config.LOGO_INTERNAL_URL + ("" if size_prefix == "" else "/") + size_prefix, files=image)