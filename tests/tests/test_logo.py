import os
import time

import requests
from sqlalchemy import text

from tests.conftest import TEST_PROXY_URL, TEST_RADIO_DNS_URL
import xml.etree.ElementTree as ET
from tests.utilities.utilities import compare_lists, sql_alchemy_result_to_list

HTML_IMAGES = [
    ['32', '32', 'http://127.0.0.1:8000/uploads/32x32/classical_music.jpg'],
    ['112', '32', 'http://127.0.0.1:8000/uploads/112x32/classical_music.jpg'],
    ['128', '128', 'http://127.0.0.1:8000/uploads/128x128/classical_music.jpg'],
    ['320', '240', 'http://127.0.0.1:8000/uploads/320x240/classical_music.jpg'],
    ['600', '600', 'http://127.0.0.1:8000/uploads/600x600/classical_music.jpg'],
    ['32', '32', 'http://127.0.0.1:8000/uploads/32x32/classical_music.png'],
    ['112', '32', 'http://127.0.0.1:8000/uploads/112x32/classical_music.png'],
    ['128', '128', 'http://127.0.0.1:8000/uploads/128x128/classical_music.png'],
    ['320', '240', 'http://127.0.0.1:8000/uploads/320x240/classical_music.png'],
    ['600', '600', 'http://127.0.0.1:8000/uploads/600x600/classical_music.png'],
]

HTML_IMAGES_NAMES = ["Classic_main", "Classic_main_2"]

MYSQL_QUERY = 'SELECT filename, url32x32, url112x32, url128x128, url320x240, url600x600, codops, "name"' \
              '          FROM logo_image'

MSQL_ROWS = [
    [
        'classical_music.jpg',
        '32x32/classical_music.jpg',
        '112x32/classical_music.jpg',
        '128x128/classical_music.jpg',
        '320x240/classical_music.jpg',
        '600x600/classical_music.jpg',
        'standalone',
        'name'
    ],
    [
        'classical_music.png',
        '32x32/classical_music.png',
        '112x32/classical_music.png',
        '128x128/classical_music.png',
        '320x240/classical_music.png',
        '600x600/classical_music.png',
        'standalone',
        'name'
    ]
]

XML_ROWS = [
    'http://127.0.0.1:8000/uploads/32x32/classical_music.jpg',
    'http://127.0.0.1:8000/uploads/112x32/classical_music.jpg',
    'http://127.0.0.1:8000/uploads/128x128/classical_music.jpg',
    'http://127.0.0.1:8000/uploads/320x240/classical_music.jpg',
    'http://127.0.0.1:8000/uploads/600x600/classical_music.jpg',
]


def test_logo(stack_setup, browser_setup):
    db = stack_setup
    driver = browser_setup
    driver.get(TEST_PROXY_URL + "serviceprovider/images/edit/-")

    # Is page loaded?
    assert ":: PlugIt -Standalone mode" == driver.title

    # Fill inputs
    driver.find_element_by_name("name").send_keys("Classic_main")
    driver.find_element_by_name("file").send_keys(os.getcwd() + "/ressources/classical_music.jpg")
    driver.find_element_by_css_selector("input[type=submit][value=Save]").click()

    driver.get(TEST_PROXY_URL + "serviceprovider/images/edit/-")
    driver.find_element_by_name("name").send_keys("Classic_main_2")
    driver.find_element_by_name("file").send_keys(os.getcwd() + "/ressources/classical_music.png")
    driver.find_element_by_css_selector("input[type=submit][value=Save]").click()

    # Check HTML
    images = list(map(
        lambda x: [x.get_attribute("naturalWidth"), x.get_attribute("naturalHeight"), x.get_attribute("currentSrc")],
        driver.find_elements_by_css_selector(".tooltipme"))
    )
    for i in range(len(images)):
        assert compare_lists(images[i], HTML_IMAGES[i], True)

    images_names = list(map(lambda x: x.text,
                            driver.find_elements_by_css_selector(".sorting_1"))
                        )
    assert compare_lists(images_names, HTML_IMAGES_NAMES, True)

    # Check DB
    result = db.engine.execute(text(MYSQL_QUERY))
    assert result.rowcount == 2
    parsed_result = sql_alchemy_result_to_list(result)
    for i in range(len(parsed_result)):
        assert compare_lists(parsed_result[i], MSQL_ROWS[i], True)

    # Select image 1 as first station logo
    driver.get(TEST_PROXY_URL + "radioepg/logos/")
    driver.find_element_by_id("logo_select").find_element_by_css_selector("option[value='1']").click()
    time.sleep(2)

    # Check XML
    res = requests.get(TEST_RADIO_DNS_URL + "radiodns/spi/3.1/SI.xml")
    assert res.status_code == 200
    xml_root = ET.fromstring(res.text)
    multimedias = list(map(lambda x: x.attrib["url"], xml_root.findall(".//{http://www.worlddab.org/schemas/spi/31}multimedia")))
    assert compare_lists(multimedias, XML_ROWS, True)
