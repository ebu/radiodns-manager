import pytest
import requests
from sqlalchemy import text

from tests.conftest import TEST_PROXY_URL, TEST_RADIO_DNS_URL
import xml.etree.ElementTree as ET
from tests.utilities.utilities import compare_lists, sql_alchemy_result_to_list

MYSQL_STATION_QUERY = "SELECT name, short_name, short_description, genres, radioepg_service, long_name, medium_name," \
                      "url_default, city, default_language, location_country, phone_number, postal_name, sms_body," \
                      "sms_description, sms_number, street, zipcode, email_address, email_description" \
                      " FROM station WHERE id = 1"

STATION_HTML_TR = [
    'Short Name CS',
    'Medium Name Classical S',
    'Long Name The mighty Classical radio',
    'Short Description The mighty Classical radioRadio is the technology of using radio waves to carry information',
    'Default Url https://github.com/ebu/PlugIt/blob/master/docs/protocol.md',
    'Default Language en-GB',
    'Postal Address EBU\nL&#39;Ancienne-Route 17A\nLe Grand-Saconnex, 1218',
    'Country France',
    'Phone Number 052 727 53 72',
    'SMS SMS description: Send SMS body to 052 727 53 72',
    'E-Mail Email description : AlexanderWexler@teleworm.us',
]

STATION_MYSQL_TR = [
    'Classical Station',
    'CS',
    'The mighty Classical radioRadio is the technology of using radio waves to carry information',
    '[{"href": "urn:tva:metadata:cs:ContentCS:2011:3.6.2", "name": "Jazz"}, {"href": "urn:tva:metadata:cs:ContentCS:2011:3.6.4.1", "name": "Pop"}]',
    'standalone.127.0.0.1:5000standalone.ebu.io',
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
    'Status: Loading',
    'FQDN: classicalstation.standalone.radio.ebu.io',
    'RadioVIS SlideShow Service Uri:',
    'RadioVIS Credentials:',
    'SPI RadioEPG Service Uri: EPG standalone.127.0.0.1:5000standalone.ebu.io',
    'Program Information Enabled: DISABLED'
]


@pytest.mark.run(order=3)
def test_create_station(stack_setup, browser_setup):
    db = stack_setup
    driver = browser_setup
    driver.get(TEST_PROXY_URL + "stations/edit/-")
    # Is page loaded?
    assert ":: PlugIt -Standalone mode" == driver.title
    # Fill inputs
    driver.find_element_by_id("station-name").send_keys("Classical Station")
    driver.find_element_by_id("short_name").clear()  # FIXME REMOVE THIS LINE ONCE OPENRADIO-23 IS SOLVED
    driver.find_element_by_id("short_name").send_keys("CS")
    driver.find_element_by_id("medium_name").clear()  # FIXME REMOVE THIS LINE ONCE OPENRADIO-23 IS SOLVED
    driver.find_element_by_id("medium_name").send_keys("Classical S")
    driver.find_element_by_id("long_name").clear()  # FIXME REMOVE THIS LINE ONCE OPENRADIO-23 IS SOLVED
    driver.find_element_by_id("long_name").send_keys("The mighty Classical radio")
    driver.find_element_by_id("short_description") \
        .send_keys("Radio is the technology of using radio waves to carry information")
    driver.find_element_by_id("copyLanguageButton").click()
    driver.find_element_by_name("url_default").send_keys("https://github.com/ebu/PlugIt/blob/master/docs/protocol.md")
    driver.find_element_by_id("copyAddressButton").click()
    driver.find_element_by_id("phone_number").send_keys("052 727 53 72")
    driver.find_element_by_id("sms_number").send_keys("052 727 53 72")
    driver.find_element_by_id("sms_body").send_keys("SMS body")
    driver.find_element_by_id("sms_description").send_keys("SMS description")
    driver.find_element_by_id("email_address").send_keys("AlexanderWexler@teleworm.us")
    driver.find_element_by_id("email_description").send_keys("Email description")
    driver.find_element_by_id("add_gender_button").click()
    driver.find_element_by_id("genre-select-0").find_element_by_css_selector("option[value='3.6.2']").click()  # Jazz
    driver.find_element_by_id("add_gender_button").click()
    driver.find_element_by_id("genre-select-1").find_element_by_css_selector("option[value='3.6.4.1']").click()  # Pop
    driver.find_element_by_id("radioepg_enabled").click()
    driver.find_element_by_id("radioepg_service").send_keys("standalone.ebu.io")
    driver.find_element_by_css_selector("input[type=submit][value=Save]").click()

    # Check entered data
    tables = driver.find_elements_by_class_name("table-responsive")
    assert len(tables) == 2
    station_tr = list(map(lambda x: x.text, tables[0].find_elements_by_css_selector("tr")))
    status_tr = list(map(lambda x: x.text, tables[1].find_elements_by_css_selector("tr")))
    assert compare_lists(station_tr, STATION_HTML_TR)
    assert compare_lists(status_tr, STATION_SERVICES_HTML_TR)

    # Check DB
    result = db.engine.execute(text(MYSQL_STATION_QUERY))
    assert result.rowcount == 1
    assert compare_lists(sql_alchemy_result_to_list(result)[0], STATION_MYSQL_TR, True)

    # Check XML
    res = requests.get(TEST_RADIO_DNS_URL + "radiodns/spi/3.1/SI.xml")
    assert res.status_code == 200
    xml_root = ET.fromstring(res.text)
    assert len(xml_root.findall(".//{http://www.worlddab.org/schemas/spi/31}service")) == 1
    assert xml_root.find(".//{http://www.worlddab.org/schemas/spi/31}shortName").text == "CS"
    assert xml_root.find(".//{http://www.worlddab.org/schemas/spi/31}mediumName").text == "Classical S"
    assert xml_root.find(".//{http://www.worlddab.org/schemas/spi/31}longName").text == "The mighty Classical radio"
    # FIXME Why does this node returns the concatenated text of the longName node and this one?
    # assert xml_root.find(".//{http://www.worlddab.org/schemas/spi/31}shortDescription")\
    #     .text == "Radio is the technology of using radio waves to carry information"
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
    assert xml_root.findall(".//{http://www.worlddab.org/schemas/spi/31}genre")[0].attrib[
               "href"] == "urn:tva:metadata:cs:ContentCS:2011:3.6.2"
    assert xml_root.findall(".//{http://www.worlddab.org/schemas/spi/31}genre")[0].text == "Jazz"
    assert xml_root.findall(".//{http://www.worlddab.org/schemas/spi/31}genre")[1].attrib[
               "href"] == "urn:tva:metadata:cs:ContentCS:2011:3.6.4.1"
    assert xml_root.findall(".//{http://www.worlddab.org/schemas/spi/31}genre")[1].text == "Pop"
