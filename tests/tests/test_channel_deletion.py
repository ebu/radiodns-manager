from functools import reduce

import pytest
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from sqlalchemy import text
import xml.etree.ElementTree as ET

from tests.conftest import TEST_PROXY_URL, TEST_RADIO_DNS_URL
from tests.test_channel_creation import CHANNELS_MSQL_QUERY
from tests.utilities.utilities import compare_lists, sql_alchemy_result_to_list, accept_alert
from selenium.webdriver.support import expected_conditions as EC

CHANNELS_HTML_TR = [
    'Station Client Type Name RadioDNS entry / Url DNS Authoritative FQDN Services',
    'Classical Station default amss CS_AMSS 4001.amss.radiodns.org. classicalstation.standalone.radio.ebu.io\nEPG standalone.ebu.io\nSPI standalone.ebu.io\nEdit Delete',
    'Classical Station default dab CS_DAB_NEW 2.4002.43e2.fe1.dab.radiodns.org. classicalstation.standalone.radio.ebu.io\nEPG standalone.ebu.io\nSPI standalone.ebu.io\nEdit Delete',
    'Classical Station default drm CS_DRM 4001.drm.radiodns.org. classicalstation.standalone.radio.ebu.io\nEPG standalone.ebu.io\nSPI standalone.ebu.io\nEdit Delete',
    'Classical Station default hd CS_HD_RADIO 0eaff.031.hd.radiodns.org. classicalstation.standalone.radio.ebu.io\nEPG standalone.ebu.io\nSPI standalone.ebu.io\nEdit Delete',
    'Classical Station default id CS_IP http://server/stream classicalstation.standalone.radio.ebu.io Edit Delete',
    'Classical Station CNN id CS_IP_2 http://server/stream/ouiiiiii classicalstation.standalone.radio.ebu.io Edit Delete'
]

CHANNELS_MYSQL_TR = [
    ' '.join(['CS_DAB_NEW', 'None', '81', '43e2', 'None', 'None', 'None', '2', 'None', '4002', 'None', 'dab', 'None', 'audio/aac', 'None', 'None']),
    ' '.join(['CS_DRM', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', '4001', 'None', 'drm', 'None', 'None', 'None', 'None']),
    ' '.join(['CS_AMSS', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', '4001', 'None', 'amss', 'None', 'None', 'None', 'None']),
    ' '.join(['CS_HD_RADIO', '031', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', '0EAFF', 'hd', 'None', 'None', 'None', 'None']),
    ' '.join(['CS_IP', 'None', 'None', 'None', 'classicalstation.standalone.radio.ebu.io', 'None', 'None', 'None', 'ebu1standalone', 'None', 'None', 'id', '200', 'audio/mpeg', 'http://server/stream', 'None']),
    ' '.join(['CS_IP_2', 'None', 'None', 'None', 'classicalstation.standalone.radio.ebu.io', 'None', 'None', 'None', 'ebu1standalone', 'None', 'None', 'id', '200', 'audio/mpeg', 'http://server/stream/ouiiiiii', '2']),
]


@pytest.mark.run(order=11)
def test_delete_channel(stack_setup, browser_setup):
    db = stack_setup
    driver = browser_setup

    driver.get(TEST_PROXY_URL + "channels/")
    driver.find_element_by_css_selector("[href='/channels/delete/2']").send_keys(Keys.RETURN)
    accept_alert(driver)
    WebDriverWait(driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "[href='/channels/delete/2']")))

    channel_tr = list(map(lambda x: x.text, driver
                          .find_element_by_id("radiodns-channel-table")
                          .find_elements_by_css_selector("tr")))
    assert compare_lists(channel_tr, CHANNELS_HTML_TR)

    # Check DB
    result = db.engine.execute(text(CHANNELS_MSQL_QUERY))
    assert result.rowcount == 6
    station_mysql_tr = []
    for row in sql_alchemy_result_to_list(result):
        station_mysql_tr.append(reduce(lambda x, y: str(x) + " " + str(y), row))
    assert compare_lists(station_mysql_tr, CHANNELS_MYSQL_TR, True)

    # Check XML
    res = requests.get(TEST_RADIO_DNS_URL + "radiodns/spi/3.1/SI.xml")
    assert res.status_code == 200
    bearers = ET.fromstring(res.text).findall(".//{http://www.worlddab.org/schemas/spi/31}bearer")
    assert len(bearers) == 5
    assert bearers[0].attrib["id"] == "amss:4001"
    assert bearers[0].attrib["cost"] == "100"
    assert bearers[1].attrib["id"] == "dab:fe1.43e2.4002.2"
    assert bearers[1].attrib["cost"] == "50"
    assert bearers[1].attrib["mimeValue"] == "audio/aac"
    assert bearers[2].attrib["id"] == "drm:4001"
    assert bearers[2].attrib["cost"] == "100"
    assert bearers[3].attrib["id"] == "hd:031.0eaff"
    assert bearers[3].attrib["cost"] == "100"
    assert bearers[4].attrib["id"] == "http://server/stream"
    assert bearers[4].attrib["cost"] == "100"
    assert bearers[4].attrib["offset"] == "2000"
    assert bearers[4].attrib["mimeValue"] == "audio/mpeg"
    assert bearers[4].attrib["bitrate"] == "200"
