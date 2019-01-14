import time
import xml.etree.ElementTree as ET

import pytest
import requests
from selenium.webdriver.common.keys import Keys
from sqlalchemy import text

from tests.conftest import TEST_PROXY_URL, TEST_RADIO_DNS_URL
from tests.utilities.utilities import compare_lists, sql_alchemy_result_to_list, set_value_of_on_blur_input, \
    create_station, accept_alert

MYSQL_STATION_QUERY_ALL = "SELECT name, short_name, short_description, genres, radioepg_service, radiospi_service," \
                      "long_name, medium_name, url_default, city, default_language, location_country, phone_number," \
                      "postal_name, sms_body, sms_description, sms_number, street, zipcode, email_address," \
                      "email_description FROM station"

MYSQL_STATION_QUERY_ONE = MYSQL_STATION_QUERY_ALL + " WHERE id = 1"

STATION_HTML_TR = [
    'Short Name CS',
    'Medium Name Classical S',
    'Long Name The mighty Classical radio',
    'Short Description Radio is the technology of using radio waves to carry information',
    'Default Url https://github.com/ebu/PlugIt/blob/master/docs/protocol.md',
    'Default Language en-GB',
    'Postal Address EBU\nL&#39;Ancienne-Route 17A\nLe Grand-Saconnex, 1218',
    'Country France',
    'Phone Number 052 727 53 72',
    'SMS SMS description : Send SMS body to 052 727 53 72',
    'E-Mail Email description : AlexanderWexler@teleworm.us',
]

STATION_MYSQL_TR = [
    'Classical Station',
    'CS',
    'Radio is the technology of using radio waves to carry information',
    '[{"href": "urn:tva:metadata:cs:ContentCS:2011:3.6.2", "name": "Jazz"}, {"href": "urn:tva:metadata:cs:ContentCS:2011:3.6.4.1", "name": "Pop"}]',
    'standalone.ebu.io',
    'standalone.ebu.io',
    'The mighty Classical radio',
    'Classical S',
    'https://github.com/ebu/PlugIt/blob/master/docs/protocol.md',
    'Le Grand-Saconnex',
    'en-GB',
    'fr',
    '052 727 53 72',
    'EBU',
    'SMS body',
    'SMS description',
    '052 727 53 72',
    'L&#39;Ancienne-Route 17A',
    '1218',
    'AlexanderWexler@teleworm.us',
    'Email description'
]

STATION_SERVICES_HTML_TR = [
    'Status: Failed',
    'FQDN: classicalstation.standalone.radio.ebu.io',
    'VIS Service Details: VIS vis disabled',
    'RadioVIS Credentials:',
    'SPI Service Details: EPG null\nSPI null',
    'Program Information Enabled: DISABLED'
]


@pytest.mark.run(order=4)
def test_create_station(stack_setup, browser_setup):
    db = stack_setup
    driver = browser_setup
    driver.get(TEST_PROXY_URL + "stations/edit/-")
    # Is page loaded?
    assert ":: PlugIt -Standalone mode" == driver.title
    # Fill inputs
    create_station(
        driver=driver,
        tab_id=0,
        station_name="Classical Station",
        short_name="CS",
        medium_name="Classical S",
        long_name="The mighty Classical radio",
        short_description="Radio is the technology of using radio waves to carry information",
        url_default="https://github.com/ebu/PlugIt/blob/master/docs/protocol.md",
        phone_number="052 727 53 72",
        sms_number="052 727 53 72",
        sms_body="SMS body",
        sms_description="SMS description",
        email_address="AlexanderWexler@teleworm.us",
        email_description="Email description",
        genres=['3.6.2', '3.6.4.1'],
        radioepg_enabled=True,
        radioepg_service="standalone.ebu.io",
        radiospi_service="standalone.ebu.io",
    )

    # Check entered data
    tables = driver.find_elements_by_class_name("table-responsive")
    assert len(tables) == 2
    station_tr = list(map(lambda x: x.text, tables[0].find_elements_by_css_selector("tr")))
    status_tr = list(map(lambda x: x.text, tables[1].find_elements_by_css_selector("tr")))
    assert compare_lists(station_tr, STATION_HTML_TR)
    assert compare_lists(status_tr, STATION_SERVICES_HTML_TR)

    # Check DB
    result = db.engine.execute(text(MYSQL_STATION_QUERY_ONE))
    assert result.rowcount == 1
    assert compare_lists(sql_alchemy_result_to_list(result)[0], STATION_MYSQL_TR, True)

    # Check XML SPI version 3
    res = requests.get(TEST_RADIO_DNS_URL + "radiodns/spi/3.1/SI.xml")
    assert res.status_code == 200
    xml_root = ET.fromstring(res.text)
    assert len(xml_root.findall(".//{http://www.worlddab.org/schemas/spi/31}service")) == 1
    assert xml_root.find(".//{http://www.worlddab.org/schemas/spi/31}shortName").text == "CS"
    assert xml_root.find(".//{http://www.worlddab.org/schemas/spi/31}mediumName").text == "Classical S"
    assert xml_root.find(".//{http://www.worlddab.org/schemas/spi/31}longName").text == "The mighty Classical radio"
    assert xml_root.find(".//{http://www.worlddab.org/schemas/spi/31}shortDescription")\
        .text == "Radio is the technology of using radio waves to carry information"
    links = xml_root.findall(".//{http://www.worlddab.org/schemas/spi/31}link")
    assert links[0].attrib["url"] == "https://github.com/ebu/PlugIt/blob/master/docs/protocol.md"
    assert links[0].attrib["mimeValue"] == "text/html"
    assert links[1].attrib["uri"] == "postal:EBU/L&#39;Ancienne-Route 17A/Le Grand-Saconnex/1218/France"
    assert links[2].attrib["uri"] == "tel:052 727 53 72"
    assert links[3].attrib["description"] == "SMS description"
    assert links[3].attrib["uri"] == "sms:052 727 53 72?body=SMS+body"
    assert links[4].attrib["description"] == "Email description"
    assert links[4].attrib["uri"] == "mailto:AlexanderWexler@teleworm.us"
    assert xml_root.find(".//{http://www.worlddab.org/schemas/spi/31}radiodns").attrib[
               "fqdn"] == "classicalstation.standalone.radio.ebu.io"
    assert xml_root.find(".//{http://www.worlddab.org/schemas/spi/31}radiodns").attrib[
               "serviceIdentifier"] == "ebu1standalone"
    multimedias = xml_root.findall(".//{http://www.worlddab.org/schemas/spi/31}multimedia")
    assert multimedias[0].attrib["height"] == "32"
    assert multimedias[0].attrib["width"] == "32"
    assert multimedias[0].attrib["type"] == "logo_colour_square"
    assert multimedias[0].attrib["url"] == ""
    assert multimedias[1].attrib["height"] == "32"
    assert multimedias[1].attrib["width"] == "112"
    assert multimedias[1].attrib["type"] == "logo_colour_rectangle"
    assert multimedias[1].attrib["url"] == ""
    assert multimedias[2].attrib["height"] == "128"
    assert multimedias[2].attrib["width"] == "128"
    assert multimedias[2].attrib["type"] == "logo_unrestricted"
    assert multimedias[2].attrib["url"] == ""
    assert multimedias[3].attrib["height"] == "240"
    assert multimedias[3].attrib["width"] == "320"
    assert multimedias[3].attrib["type"] == "logo_unrestricted"
    assert multimedias[3].attrib["url"] == ""
    assert multimedias[4].attrib["height"] == "600"
    assert multimedias[4].attrib["width"] == "600"
    assert multimedias[4].attrib["type"] == "logo_unrestricted"
    assert multimedias[4].attrib["url"] == ""
    assert xml_root.findall(".//{http://www.worlddab.org/schemas/spi/31}genre")[1].attrib[
               "href"] == "urn:tva:metadata:cs:ContentCS:2011:3.6.4.1"
    assert xml_root.findall(".//{http://www.worlddab.org/schemas/spi/31}genre")[1].text == "Pop"
    assert xml_root.findall(".//{http://www.worlddab.org/schemas/spi/31}genre")[0].attrib[
               "href"] == "urn:tva:metadata:cs:ContentCS:2011:3.6.2"
    assert xml_root.findall(".//{http://www.worlddab.org/schemas/spi/31}genre")[0].text == "Jazz"

    # Check XML SPI version 1
    res = requests.get(TEST_RADIO_DNS_URL + "radiodns/epg/XSI.xml")
    assert res.status_code == 200
    xml_root = ET.fromstring(res.text)
    assert len(xml_root.findall(".//{http://schemas.radiodns.org/epg/11}service")) == 1
    assert xml_root.find(".//{http://www.worlddab.org/schemas/epgDataTypes/14}shortName").text == "CS"
    assert xml_root.find(".//{http://www.worlddab.org/schemas/epgDataTypes/14}mediumName").text == "Classical S"
    assert xml_root.find(".//{http://www.worlddab.org/schemas/epgDataTypes/14}longName").text == "The mighty Classical radio"
    assert xml_root.find(".//{http://www.worlddab.org/schemas/epgDataTypes/14}shortDescription") \
               .text == "Radio is the technology of using radio waves to carry information"
    assert xml_root.find(".//{http://www.worlddab.org/schemas/epgDataTypes/14}link").attrib[
               "url"] == "https://github.com/ebu/PlugIt/blob/master/docs/protocol.md"
    assert xml_root.find(".//{http://www.worlddab.org/schemas/epgDataTypes/14}link").attrib["mimeValue"] == "text/html"
    assert xml_root.find(".//{http://schemas.radiodns.org/epg/11}radiodns").attrib[
               "fqdn"] == "classicalstation.standalone.radio.ebu.io"
    assert xml_root.find(".//{http://schemas.radiodns.org/epg/11}radiodns").attrib[
               "serviceIdentifier"] == "ebu1standalone"
    multimedias = xml_root.findall(".//{http://www.worlddab.org/schemas/epgDataTypes/14}multimedia")
    assert multimedias[0].attrib["height"] == "32"
    assert multimedias[0].attrib["width"] == "32"
    assert multimedias[0].attrib["type"] == "logo_colour_square"
    assert multimedias[0].attrib["url"] == ""
    assert multimedias[1].attrib["height"] == "32"
    assert multimedias[1].attrib["width"] == "112"
    assert multimedias[1].attrib["type"] == "logo_unrestricted"
    assert multimedias[1].attrib["url"] == ""
    assert multimedias[2].attrib["height"] == "128"
    assert multimedias[2].attrib["width"] == "128"
    assert multimedias[2].attrib["type"] == "logo_unrestricted"
    assert multimedias[2].attrib["url"] == ""
    assert multimedias[3].attrib["height"] == "240"
    assert multimedias[3].attrib["width"] == "320"
    assert multimedias[3].attrib["type"] == "logo_unrestricted"
    assert multimedias[3].attrib["url"] == ""
    assert multimedias[4].attrib["height"] == "600"
    assert multimedias[4].attrib["width"] == "600"
    assert multimedias[4].attrib["type"] == "logo_unrestricted"
    assert multimedias[4].attrib["url"] == ""
    assert xml_root.findall(".//{http://www.worlddab.org/schemas/epgDataTypes/14}genre")[1].attrib[
               "href"] == "urn:tva:metadata:cs:ContentCS:2011:3.6.4.1"
    assert xml_root.findall(".//{http://www.worlddab.org/schemas/epgDataTypes/14}name")[1].text == "Pop"
    assert xml_root.findall(".//{http://www.worlddab.org/schemas/epgDataTypes/14}genre")[0].attrib[
               "href"] == "urn:tva:metadata:cs:ContentCS:2011:3.6.2"
    assert xml_root.findall(".//{http://www.worlddab.org/schemas/epgDataTypes/14}name")[0].text == "Jazz"


@pytest.mark.second_to_last
def test_delete_station(stack_setup, browser_setup):
    db = stack_setup
    driver = browser_setup
    
    driver.get(TEST_PROXY_URL + "stations/edit/-")
    create_station(
        save=False,
        driver=driver,
        tab_id=0,
        station_name="WILL BE DELETED4",
    )
    driver.find_element_by_id("nav_tab_1").send_keys(Keys.RETURN)
    create_station(
        driver=driver,
        tab_id=1,
        station_name="WILL BE DELETED5",
    )

    driver.get(TEST_PROXY_URL + "stations/edit/-")
    create_station(
        driver=driver,
        tab_id=0,
        station_name="WILL BE DELETED6",
    )

    driver.get(TEST_PROXY_URL + "stations/edit/-")
    create_station(
        save=False,
        driver=driver,
        tab_id=0,
        station_name="WILL BE DELETED7",
    )
    driver.find_element_by_id("nav_tab_1").send_keys(Keys.RETURN)
    create_station(
        driver=driver,
        tab_id=1,
        station_name="WILL BE DELETED8",
    )

    result = db.engine.execute(text(MYSQL_STATION_QUERY_ALL))
    assert result.rowcount == 8

    driver.get(TEST_PROXY_URL + "stations/4")
    driver.find_element_by_css_selector('[href="/plugIt/stations/delete/4"]').send_keys(Keys.RETURN)
    accept_alert(driver)
    time.sleep(2)
    result = db.engine.execute(text(MYSQL_STATION_QUERY_ALL))
    assert result.rowcount == 6
    assert db.engine.execute(text("SELECT id FROM station WHERE id=4")).rowcount == 0

    driver.get(TEST_PROXY_URL + "stations/")
    driver.find_element_by_css_selector('[href="/plugIt/stations/delete/6"]').send_keys(Keys.RETURN)
    accept_alert(driver)
    time.sleep(2)
    result = db.engine.execute(text(MYSQL_STATION_QUERY_ALL))
    assert result.rowcount == 5
    assert db.engine.execute(text("SELECT id FROM station WHERE id=6")).rowcount == 0

    driver.get(TEST_PROXY_URL + "stations/edit/7")
    driver.find_element_by_css_selector('[onclick="StationModuleEdit.prototype.deleteStation(1)"]').send_keys(Keys.RETURN)
    accept_alert(driver)
    time.sleep(2)
    result = db.engine.execute(text(MYSQL_STATION_QUERY_ALL))
    assert result.rowcount == 4
    assert db.engine.execute(text("SELECT id FROM station WHERE id=8")).rowcount == 0
