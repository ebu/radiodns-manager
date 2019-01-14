from functools import reduce

import pytest
import requests
import xml.etree.ElementTree as ET

from selenium.webdriver.support.select import Select
from sqlalchemy import text

from tests.conftest import TEST_PROXY_URL, TEST_RADIO_DNS_URL
from tests.test_channel_creation import CHANNELS_MSQL_QUERY
from tests.utilities.utilities import clear_input, compare_lists, sql_alchemy_result_to_list

CHANNELS_HTML_TR = [
    'Station Client Type Name RadioDNS entry / Url DNS Authoritative FQDN Services',
    'Classical Station default amss CS_AMSS 4001.amss.radiodns.org. classicalstation.standalone.radio.ebu.io\nEPG standalone.ebu.io\nSPI standalone.ebu.io\nEdit Delete',
    'Classical Station default dab CS_DAB 0.4001.43e1.fe1.dab.radiodns.org. classicalstation.standalone.radio.ebu.io\nEPG standalone.ebu.io\nSPI standalone.ebu.io\nEdit Delete',
    'Classical Station default drm CS_DRM 4001.drm.radiodns.org. classicalstation.standalone.radio.ebu.io\nEPG standalone.ebu.io\nSPI standalone.ebu.io\nEdit Delete',
    'Classical Station default dab CS_DAB_NEW 2.4002.43e2.fe1.dab.radiodns.org. classicalstation.standalone.radio.ebu.ioEPG standalone.ebu.ioSPI standalone.ebu.ioEdit Delete',
    'Classical Station default hd CS_HD_RADIO 0eaff.9e0.hd.radiodns.org. classicalstation.standalone.radio.ebu.io\nEPG standalone.ebu.io\nSPI standalone.ebu.io\nEdit Delete',
    'Classical Station default id CS_IP http://server/stream classicalstation.standalone.radio.ebu.io Edit Delete',
    'Classical Station CNN id CS_IP_2 http://server/stream/ouiiiiii classicalstation.standalone.radio.ebu.io Edit Delete'
]

CHANNELS_MYSQL_TR = [
    ' '.join(['CS_DAB_NEW', 'None', '81', '43e2', 'None', 'None', 'None', '2', 'None', '4002', 'None', 'dab', 'None', 'audio/aac', 'None', 'None']),
    ' '.join(['CS_DAB', 'None', '81', '43e1', 'None', 'None', 'None', '0', 'None', '4001', 'None', 'dab', 'None', 'audio/mpeg', 'None', 'None']),
    ' '.join(['CS_DRM', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', '4001', 'None', 'drm', 'None', 'None', 'None', 'None']),
    ' '.join(['CS_AMSS', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', '4001', 'None', 'amss', 'None', 'None', 'None', 'None']),
    ' '.join(['CS_HD_RADIO', '9E0', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', '0EAFF', 'hd', 'None', 'None', 'None', 'None']),
    ' '.join(['CS_IP', 'None', 'None', 'None', 'classicalstation.standalone.radio.ebu.io', 'None', 'None', 'None', 'ebu1standalone', 'None', 'None', 'id', '200', 'audio/mpeg', 'http://server/stream', 'None']),
    ' '.join(['CS_IP_2', 'None', 'None', 'None', 'classicalstation.standalone.radio.ebu.io', 'None', 'None', 'None', 'ebu1standalone', 'None', 'None', 'id', '200', 'audio/mpeg', 'http://server/stream/ouiiiiii', '2']),
]


@pytest.mark.run(order=10)
def test_channel_edition(stack_setup, browser_setup):
    db = stack_setup
    driver = browser_setup
    
    driver.get(TEST_PROXY_URL + "channels/edit/1")
    assert Select(driver.find_element_by_name("station")).first_selected_option.get_attribute('value') == "1"
    assert driver.find_element_by_name("name").get_attribute("value") == "CS_VHF_FM"
    assert Select(driver.find_element_by_name("fk_client")).first_selected_option.text.strip() == "default"
    assert Select(driver.find_element_by_name("type_id")).first_selected_option.text.strip() == "VHF/FM"
    assert Select(driver.find_element_by_name("ecc_id")).first_selected_option.text.strip() == "France (FR) [FE1]"  # CH 4EI
    assert driver.find_element_by_name("pi").get_attribute('value') == "C00F"
    assert driver.find_element_by_name("frequency").get_attribute('value') == "00917"

    clear_input(driver, "[name=name]")
    driver.find_element_by_name("name").send_keys("CS_DAB_NEW")
    driver.find_element_by_id("type").find_element_by_css_selector("option[value=dab]").click()
    driver.find_element_by_name("eid").send_keys("43e2")
    driver.find_element_by_name("sid").send_keys("4002")
    driver.find_element_by_name("scids").send_keys("2")
    driver.find_element_by_name("mime_type").send_keys("audio/aac")
    driver.find_element_by_css_selector("input[type=submit][value=Save]").click()

    # Check entered data
    channel_tr = list(map(lambda x: x.text, driver
                          .find_element_by_id("radiodns-channel-table")
                          .find_elements_by_css_selector("tr")))
    assert compare_lists(channel_tr, CHANNELS_HTML_TR)

    # Check DB
    result = db.engine.execute(text(CHANNELS_MSQL_QUERY))
    assert result.rowcount == 7
    station_mysql_tr = []
    for row in sql_alchemy_result_to_list(result):
        station_mysql_tr.append(reduce(lambda x, y: str(x) + " " + str(y), row))
    assert compare_lists(station_mysql_tr, CHANNELS_MYSQL_TR, True)

    # Check XML
    res = requests.get(TEST_RADIO_DNS_URL + "radiodns/spi/3.1/SI.xml")
    assert res.status_code == 200
    bearers = ET.fromstring(res.text).findall(".//{http://www.worlddab.org/schemas/spi/31}bearer")
    assert len(bearers) == 6
    assert bearers[0].attrib["id"] == "amss:4001"
    assert bearers[0].attrib["cost"] == "100"
    assert bearers[1].attrib["id"] == "dab:fe1.43e1.4001.0"
    assert bearers[1].attrib["cost"] == "20"
    assert bearers[1].attrib["mimeValue"] == "audio/mpeg"
    assert bearers[2].attrib["id"] == "dab:fe1.43e2.4002.2"
    assert bearers[2].attrib["cost"] == "50"
    assert bearers[2].attrib["mimeValue"] == "audio/aac"
    assert bearers[3].attrib["id"] == "drm:4001"
    assert bearers[3].attrib["cost"] == "100"
    assert bearers[4].attrib["id"] == "hd:9e0.0eaff"
    assert bearers[4].attrib["cost"] == "100"
    assert bearers[5].attrib["id"] == "http://server/stream"
    assert bearers[5].attrib["cost"] == "100"
    assert bearers[5].attrib["offset"] == "2000"
    assert bearers[5].attrib["mimeValue"] == "audio/mpeg"
    assert bearers[5].attrib["bitrate"] == "200"
