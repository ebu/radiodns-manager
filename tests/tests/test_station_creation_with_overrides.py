import http
import time
import xml.etree.ElementTree as ET

import pytest
from selenium.webdriver.common.keys import Keys
from sqlalchemy import text

from tests.conftest import TEST_PROXY_URL, TEST_RADIO_DNS_PORT
from tests.utilities.utilities import compare_lists, sql_alchemy_result_to_list, set_value_of_on_blur_input, \
    create_station

MYSQL_STATION_QUERY = "SELECT name, short_name, short_description, genres, radioepg_service, long_name, medium_name," \
                      "url_default, city, default_language, location_country, phone_number, postal_name, sms_body," \
                      "sms_description, sms_number, street, zipcode, email_address, email_description" \
                      " FROM station WHERE id = 3"

STATION_DETAILS_DEFAULT_TR = [
    'Short Name CS2',
    'Medium Name CS2',
    'Long Name CS2',
    'Short Description CS2',
    'Default Url',
    'Default Language en-GB',
    'Postal Address',
    'Country Switzerland',
    'Phone Number',
    'SMS',
    'E-Mail'
]

STATION_DETAILS_OVERRIDES_TR = [
    'Short Name sno',
    'Medium Name sno',
    'Long Name long name override',
    'Short Description short description override',
    'Default Url https://github.com/ebu',
    'Default Language fr',
    'Postal Address postal name override\nstreet override\ncity override, 1110',
    'Country Azores [Portugal]',
    'Phone Number 1111111111',
    'SMS SMS description override : Send SMS body override to 222222222',
    'E-Mail Email description override : AlexanderWexler@teleworm.us override',
]

STATION_DATABASE_OVERRIDES_TR = [
    'station name override',
    'sno',
    'short description override',
    '[{"href": "urn:tva:metadata:cs:ContentCS:2011:3.1.1.12", "name": "Traffic"}, {"href": "urn:tva:metadata:cs:ContentCS:2011:3.3.5", "name": "Travel"}, {"href": "urn:tva:metadata:cs:ContentCS:2011:3.6.4.14.2", "name": "Metal"}]',
    None,
    'long name override',
    'sno',
    'https://github.com/ebu',
    'city override',
    'fr',
    'pt',
    '1111111111',
    'postal name override',
    'SMS body override',
    'SMS description override',
    '222222222',
    'street override',
    '1110',
    'AlexanderWexler@teleworm.us override',
    'Email description override'
]


def check_station_override_values(db, driver):
    """
    Verifies the values for this test's suite overrides.

    :param db: The sqlalchemy database connection.
    :param driver: The Selenium WebDriver instance.
    :return: -
    """
    # go to details
    driver.get(TEST_PROXY_URL + "stations/2")

    # Check html
    tables = driver.find_elements_by_class_name("table-responsive")
    assert len(tables) == 3
    station_tr = list(map(lambda x: x.text, tables[0].find_elements_by_css_selector("tr")))
    driver.find_element_by_id("nav_tab_2").send_keys(Keys.RETURN)
    overrides_tr = list(map(lambda x: x.text, tables[2].find_elements_by_css_selector("tr")))
    assert compare_lists(station_tr, STATION_DETAILS_DEFAULT_TR)
    assert compare_lists(overrides_tr, STATION_DETAILS_OVERRIDES_TR)

    # Check DB
    result = db.engine.execute(text(MYSQL_STATION_QUERY))
    assert result.rowcount == 1
    assert compare_lists(sql_alchemy_result_to_list(result)[0], STATION_DATABASE_OVERRIDES_TR, True)

    # Check XML
    conn = http.client.HTTPConnection("localhost", TEST_RADIO_DNS_PORT)
    conn.request('GET', '/radiodns/spi/3.1/SI.xml', headers={"Authorization": "ClientIdentifier TESTIDENTIFIERS2"})
    res = conn.getresponse()
    assert res.code == 200
    xml_root = ET.fromstring(res.read().decode())
    assert len(xml_root.findall(".//{http://www.worlddab.org/schemas/spi/31}service")) == 2

    # Select the station that is an override
    xml_root = xml_root.findall(".//{http://www.worlddab.org/schemas/spi/31}service")[1]
    assert xml_root.find(".//{http://www.worlddab.org/schemas/spi/31}shortName").text == "sno"
    assert xml_root.find(".//{http://www.worlddab.org/schemas/spi/31}mediumName").text == "sno"
    assert xml_root.find(".//{http://www.worlddab.org/schemas/spi/31}longName").text == "long name override"

    links = xml_root.findall(".//{http://www.worlddab.org/schemas/spi/31}link")
    assert links[0].attrib["url"] == "https://github.com/ebu"
    assert links[0].attrib["mimeValue"] == "text/html"
    assert links[1].attrib["uri"] == "postal:postal name override/street override/city override/1110/Azores [Portugal]"
    assert links[2].attrib["uri"] == "tel:1111111111"
    assert links[3].attrib["description"] == "SMS description override"
    assert links[3].attrib["uri"] == "sms:222222222?body=SMS+body+override"
    assert links[4].attrib["description"] == "Email description override"
    assert links[4].attrib["uri"] == "mailto:AlexanderWexler@teleworm.us override"
    assert xml_root.find(".//{http://www.worlddab.org/schemas/spi/31}radiodns").attrib[
               "fqdn"] == "stationnameoverride.standalone.radio.ebu.io"
    assert xml_root.find(".//{http://www.worlddab.org/schemas/spi/31}radiodns").attrib[
               "serviceIdentifier"] == "ebu2standalone"

    multimedias = xml_root.findall(".//{http://www.worlddab.org/schemas/spi/31}multimedia")
    assert multimedias[0].attrib["height"] == "32"
    assert multimedias[0].attrib["width"] == "32"
    assert multimedias[0].attrib["type"] == "logo_colour_square"
    assert multimedias[0].attrib["url"] == "http://127.0.0.1:8001/uploads/32x32/classical_music.png"
    assert multimedias[1].attrib["height"] == "32"
    assert multimedias[1].attrib["width"] == "112"
    assert multimedias[1].attrib["type"] == "logo_colour_rectangle"
    assert multimedias[1].attrib["url"] == "http://127.0.0.1:8001/uploads/112x32/classical_music.png"
    assert multimedias[2].attrib["height"] == "128"
    assert multimedias[2].attrib["width"] == "128"
    assert multimedias[2].attrib["type"] == "logo_unrestricted"
    assert multimedias[2].attrib["url"] == "http://127.0.0.1:8001/uploads/128x128/classical_music.png"
    assert multimedias[3].attrib["height"] == "240"
    assert multimedias[3].attrib["width"] == "320"
    assert multimedias[3].attrib["type"] == "logo_unrestricted"
    assert multimedias[3].attrib["url"] == "http://127.0.0.1:8001/uploads/320x240/classical_music.png"
    assert multimedias[4].attrib["height"] == "600"
    assert multimedias[4].attrib["width"] == "600"
    assert multimedias[4].attrib["type"] == "logo_unrestricted"
    assert multimedias[4].attrib["url"] == "http://127.0.0.1:8001/uploads/600x600/classical_music.png"

    genres = xml_root.findall(".//{http://www.worlddab.org/schemas/spi/31}genre")
    assert len(genres) == 3
    assert genres[0].attrib["href"] == "urn:tva:metadata:cs:ContentCS:2011:3.1.1.12"
    assert genres[0].text == "Traffic"
    assert genres[1].attrib["href"] == "urn:tva:metadata:cs:ContentCS:2011:3.3.5"
    assert genres[1].text == "Travel"
    assert genres[2].attrib["href"] == "urn:tva:metadata:cs:ContentCS:2011:3.6.4.14.2"
    assert genres[2].text == "Metal"


@pytest.mark.run(order=6)
def test_station_creation_with_overrides(stack_setup, browser_setup):
    db = stack_setup
    driver = browser_setup
    driver.get(TEST_PROXY_URL + "stations/edit/-")

    # Fill inputs
    create_station(
        driver=driver,
        tab_id=0,
        save=False,
        station_name="Classical Station 2",
        short_name="CS2",
        medium_name="CS2",
        long_name="CS2",
        short_description="CS2",
        address={'postal_name': '', 'street': '', 'zipcode': '', 'city': '', 'location_country': 'ch'},
        genres=['3.6.4.14', '3.6.10', '3.6.4.14.2'],
        radioepg_enabled=True,
        radioepg_service="standalone.ebu.io",
        radiospi_service="standalone.ebu.io",
    )

    # Fill inputs for override
    driver.find_element_by_id("nav_tab_2").send_keys(Keys.RETURN)
    create_station(
        driver=driver,
        tab_id=2,
        save=False,
        station_name="station name override",
        short_name="sno",
        medium_name="sno",
        long_name="long name override",
        short_description="short description override",
        default_language='fr',
        email_address='AlexanderWexler@teleworm.us override',
        sms_description="SMS description override",
        sms_body='SMS body override',
        sms_number="222222222",
        phone_number='1111111111',
        email_description='Email description override',
        url_default="https://github.com/ebu",
        address={'postal_name': 'postal name override',
                 'street': 'street override',
                 'zipcode': '1110',
                 'city': 'city override',
                 'location_country': 'pt',
                 },
    )

    driver.find_element_by_id("genre_row_template_2-0").find_element_by_css_selector(
        "option[value='3.3.5']").click()  # Travel
    driver.find_element_by_id("genre_row_template_2-1").find_element_by_css_selector(
        ".btn.btn-xs.btn-danger").click()
    driver.find_element_by_id("genre_row_template_2-2").find_element_by_css_selector(
        ".btn.btn-xs.btn-danger").click()

    driver.find_element_by_id("add_gender_button_2").click()
    driver.find_element_by_id("genre_row_template_2-4").find_element_by_css_selector(
        "option[value='3.6.4.14.2']").click()  # Metal
    driver.find_element_by_id("add_gender_button_2").click()
    driver.find_element_by_id("genre_row_template_2-5").find_element_by_css_selector(
        "option[value='3.1.1.12']").click()  # Traffic

    driver.find_element_by_css_selector("button[type=submit][value=Save]").click()

    # Set logos for station
    driver.get(TEST_PROXY_URL + "radioepg/logos/")
    assert len(driver.find_elements_by_id("logo_select")) == 3
    driver.find_elements_by_id("logo_select")[1].find_element_by_css_selector("option[value='1']").click()
    driver.find_elements_by_id("logo_select")[2].find_element_by_css_selector("option[value='2']").click()
    time.sleep(1)

    check_station_override_values(db, driver)
