import http
import xml.etree.ElementTree as ET

import pytest
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from sqlalchemy import text

from tests.conftest import TEST_PROXY_URL, TEST_RADIO_DNS_PORT
from tests.test_station_creation_with_overrides import check_station_override_values
from tests.utilities.utilities import compare_lists, sql_alchemy_result_to_list

MYSQL_STATION_QUERY = "SELECT name, short_name, short_description, genres, radioepg_service, long_name, medium_name," \
                      "url_default, city, default_language, location_country, phone_number, postal_name, sms_body," \
                      "sms_description, sms_number, street, zipcode, email_address, email_description" \
                      " FROM station WHERE id = 3"

STATION_DETAILS_DEFAULT_TR = [
    'Short Name snom',
    'Medium Name snom',
    'Long Name Modified',
    'Short Description Modified',
    'Default Url Modified url',
    'Default Language it',
    'Postal Address Modified postal name\nModified street\nModified city, Modified zipcode',
    'Country Liechtenstein',
    'Phone Number Modified phone number',
    'SMS Modified description : Send Modified sms body to Modified sms number',
    'E-Mail Modified description : Modified email',
]

STATION_DETAILS_OVERRIDES_TR = [
    'Short Name snomo',
    'Medium Name snomo',
    'Long Name long name overrideModified Override',
    'Short Description short description overrideModified Override',
    'Default Url https://github.com/ebuModified Override',
    'Default Language fr',
    'Postal Address postal name overrideModified Override\nstreet overrideModified Override\ncity overrideModified Override, 1110Modified Override',
    'Country Azores [Portugal]',
    'Phone Number 1111111111Modified Override',
    'SMS SMS description overrideModified Override : Send SMS body overrideModified Override to 222222222Modified Override',
    'E-Mail Email description overrideModified Override : AlexanderWexler@teleworm.us overrideModified Override'
]

STATION_DATABASE_OVERRIDES_TR = [
    'station name overrideModified Override',
    'snomo',
    'short description overrideModified Override',
    '[{"href": "urn:tva:metadata:cs:ContentCS:2011:3.1.1.13", "name": "Weather forecasts"}, {"href": "urn:tva:metadata:cs:ContentCS:2011:3.1.1.16", "name": "Current Affairs"}, {"href": "urn:tva:metadata:cs:ContentCS:2011:3.6.4", "name": "Pop-rock"}]',
    None,
    'long name overrideModified Override',
    'snomo',
    'https://github.com/ebuModified Override',
    'city overrideModified Override',
    'fr',
    'pt',
    '1111111111Modified Override',
    'postal name overrideModified Override',
    'SMS body overrideModified Override',
    'SMS description overrideModified Override',
    '222222222Modified Override',
    'street overrideModified Override',
    '1110Modified Override',
    'AlexanderWexler@teleworm.us overrideModified Override',
    'Email description overrideModified Override',
]


@pytest.mark.run(order=7)
def test_station_edition_overrides_no_changes(stack_setup, browser_setup):
    db = stack_setup
    driver = browser_setup

    driver.get(TEST_PROXY_URL + "stations/edit/2")
    overrides_tabs = driver.find_elements_by_class_name("nav-item")

    assert len(overrides_tabs) == 3

    assert "override" not in overrides_tabs[1].get_attribute('class').split()
    assert "override" in overrides_tabs[2].get_attribute('class').split()

    assert len(driver.find_elements_by_css_selector(".btn.btn-danger.btn-close")) == 1
    overrides_tabs[2].find_elements_by_css_selector(".btn.btn-danger.btn-close")

    WebDriverWait(driver, 5).until(
        lambda x: x.find_element_by_id("location_country_0")
            .find_element_by_css_selector("option[value=hk]"))
    check_station_override_values(db, driver)


@pytest.mark.run(order=8)
def test_station_edition_with_overrides(stack_setup, browser_setup):
    db = stack_setup
    driver = browser_setup

    driver.get(TEST_PROXY_URL + "stations/edit/2")

    # Modify inputs, remove the last genre.
    driver.find_element_by_id("station-name_0").send_keys("Modified")
    driver.find_element_by_id("short_name_0").clear()
    driver.find_element_by_id("short_name_0").send_keys("snom")
    driver.find_element_by_id("medium_name_0").clear()
    driver.find_element_by_id("medium_name_0").send_keys("snom")
    driver.find_element_by_id("long_name_0").clear()
    driver.find_element_by_id("long_name_0").send_keys("Modified")
    driver.find_element_by_id("short_description_0").clear()
    driver.find_element_by_id("short_description_0").send_keys("Modified")
    driver.find_element_by_id("default_language_0").find_element_by_css_selector("option[value='it']").click()
    driver.find_element_by_name("url_default_0").send_keys("Modified url")
    driver.find_element_by_id("postal_name_0").send_keys("Modified postal name")
    driver.find_element_by_id("street_0").send_keys("Modified street")
    driver.find_element_by_id("zipcode_0").send_keys("Modified zipcode")
    driver.find_element_by_id("city_0").send_keys("Modified city")
    driver.find_element_by_id("location_country_0").find_element_by_css_selector("option[value='li']").click()
    driver.find_element_by_id("phone_number_0").send_keys("Modified phone number")
    driver.find_element_by_id("sms_number_0").send_keys("Modified sms number")
    driver.find_element_by_id("sms_body_0").send_keys("Modified sms body")
    driver.find_element_by_id("sms_description_0").send_keys("Modified description")
    driver.find_element_by_id("email_address_0").send_keys("Modified email")
    driver.find_element_by_id("email_description_0").send_keys("Modified description")

    driver.find_element_by_id("genre_row_template_0-0").find_element_by_css_selector(
        "option[value='3.1.1']").click()  # News
    driver.find_element_by_id("add_gender_button_0").click()
    driver.find_element_by_id("genre_row_template_0-1").find_element_by_css_selector(
        "option[value='3.1.1.11']").click()  # Local/Regional
    driver.find_element_by_id("genre_row_template_0-2").find_element_by_css_selector(
        ".btn.btn-xs.btn-danger").click()

    driver.find_element_by_id("nav_tab_1").send_keys(Keys.RETURN)
    # Check overrides indicator visibility
    assert driver.find_element_by_id("dot_grp_1_name").get_attribute("style") == ""
    assert driver.find_element_by_id("dot_grp_1_language").get_attribute("style") == ""
    assert driver.find_element_by_id("dot_grp_1_links").get_attribute("style") == ""
    assert driver.find_element_by_id("dot_grp_1_address").get_attribute("style") == ""
    assert driver.find_element_by_id("dot_grp_1_contact").get_attribute("style") == ""
    assert driver.find_element_by_id("dot_grp_1_genres").get_attribute("style") == ""

    driver.find_element_by_id("nav_tab_2").send_keys(Keys.RETURN)
    # Check overrides indicator visibility
    assert driver.find_element_by_id("dot_grp_2_name").get_attribute("style") == "opacity: 1;"
    assert driver.find_element_by_id("dot_grp_2_language").get_attribute("style") == "opacity: 1;"
    assert driver.find_element_by_id("dot_grp_2_links").get_attribute("style") == "opacity: 1;"
    assert driver.find_element_by_id("dot_grp_2_address").get_attribute("style") == "opacity: 1;"
    assert driver.find_element_by_id("dot_grp_2_contact").get_attribute("style") == "opacity: 1;"
    assert driver.find_element_by_id("dot_grp_2_genres").get_attribute("style") == "opacity: 1;"

    # Assert that overridden inputs are not changed even if the defaults one have.
    assert driver.find_element_by_id("station-name_2").get_attribute("value") == "station name override"
    assert driver.find_element_by_id("short_name_2").get_attribute("value") == "sno"
    assert driver.find_element_by_id("medium_name_2").get_attribute("value") == "sno"
    assert driver.find_element_by_id("long_name_2").get_attribute("value") == "long name override"
    assert driver.find_element_by_id("short_description_2").get_attribute("value") == "short description override"
    assert Select(driver.find_element_by_id("default_language_2"))\
               .first_selected_option.get_attribute("value") == "fr"
    assert driver.find_element_by_name("url_default_2").get_attribute("value") == "https://github.com/ebu"
    assert driver.find_element_by_id("postal_name_2").get_attribute("value") == "postal name override"
    assert driver.find_element_by_id("street_2").get_attribute("value") == "street override"
    assert driver.find_element_by_id("zipcode_2").get_attribute("value") == "1110"
    assert driver.find_element_by_id("city_2").get_attribute("value") == "city override"
    assert Select(driver.find_element_by_id("location_country_2"))\
               .first_selected_option.get_attribute("value") == "pt"
    assert driver.find_element_by_id("phone_number_2").get_attribute("value") == "1111111111"
    assert driver.find_element_by_id("sms_number_2").get_attribute("value") == "222222222"
    assert driver.find_element_by_id("sms_body_2").get_attribute("value") == "SMS body override"
    assert driver.find_element_by_id("sms_description_2").get_attribute("value") == "SMS description override"
    assert driver.find_element_by_id("email_address_2").get_attribute("value") == "AlexanderWexler@teleworm.us override"
    assert driver.find_element_by_id("email_description_2").get_attribute("value") == "Email description override"

    assert Select(driver.find_element_by_id("genre_row_template_2-0").find_element_by_tag_name("select"))\
               .first_selected_option.get_attribute("value") == "3.1.1.12"
    assert Select(driver.find_element_by_id("genre_row_template_2-1").find_element_by_tag_name("select")) \
               .first_selected_option.get_attribute("value") == "3.3.5"
    assert Select(driver.find_element_by_id("genre_row_template_2-2").find_element_by_tag_name("select")) \
               .first_selected_option.get_attribute("value") == "3.6.4.14.2"

    # Change override's values
    driver.find_element_by_id("station-name_2").send_keys("Modified Override")
    driver.find_element_by_id("short_name_2").send_keys("mo")
    driver.find_element_by_id("medium_name_2").send_keys("mo")
    driver.find_element_by_id("long_name_2").send_keys("Modified Override")
    driver.find_element_by_id("short_description_2").send_keys("Modified Override")
    driver.find_element_by_id("default_language_2").find_element_by_css_selector("option[value='fr']").click()
    driver.find_element_by_name("url_default_2").send_keys("Modified Override")
    driver.find_element_by_id("postal_name_2").send_keys("Modified Override")
    driver.find_element_by_id("street_2").send_keys("Modified Override")
    driver.find_element_by_id("zipcode_2").send_keys("Modified Override")
    driver.find_element_by_id("city_2").send_keys("Modified Override")
    driver.find_element_by_id("location_country_2").find_element_by_css_selector("option[value='pt']").click()
    driver.find_element_by_id("phone_number_2").send_keys("Modified Override")
    driver.find_element_by_id("sms_number_2").send_keys("Modified Override")
    driver.find_element_by_id("sms_body_2").send_keys("Modified Override")
    driver.find_element_by_id("sms_description_2").send_keys("Modified Override")
    driver.find_element_by_id("email_address_2").send_keys("Modified Override")
    driver.find_element_by_id("email_description_2").send_keys("Modified Override")

    driver.find_element_by_id("genre_row_template_2-0").find_element_by_css_selector(
        "option[value='3.1.1.13']").click()  # Weather forecasts
    driver.find_element_by_id("genre_row_template_2-1").find_element_by_css_selector(
        "option[value='3.1.1.16']").click()  # Current Affairs
    driver.find_element_by_id("genre_row_template_2-2").find_element_by_css_selector(
        "option[value='3.6.4']").click()  # Pop-rock

    driver.find_element_by_css_selector("button[type=submit][value=Save]").click()

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
    assert xml_root.find(".//{http://www.worlddab.org/schemas/spi/31}shortName").text == "snomo"
    assert xml_root.find(".//{http://www.worlddab.org/schemas/spi/31}mediumName").text == "snomo"
    assert xml_root.find(".//{http://www.worlddab.org/schemas/spi/31}longName").text == "long name overrideModified Override"

    links = xml_root.findall(".//{http://www.worlddab.org/schemas/spi/31}link")
    assert links[0].attrib["url"] == "https://github.com/ebuModified Override"
    assert links[0].attrib["mimeValue"] == "text/html"
    assert links[1].attrib["uri"] == "postal:postal name overrideModified Override/street overrideModified Override/city overrideModified Override/1110Modified Override/Azores [Portugal]"
    assert links[2].attrib["uri"] == "tel:1111111111Modified Override"
    assert links[3].attrib["description"] == "SMS description overrideModified Override"
    assert links[3].attrib["uri"] == "sms:222222222Modified Override?body=SMS+body+overrideModified+Override"
    assert links[4].attrib["description"] == "Email description overrideModified Override"
    assert links[4].attrib["uri"] == "mailto:AlexanderWexler@teleworm.us overrideModified Override"
    assert xml_root.find(".//{http://www.worlddab.org/schemas/spi/31}radiodns").attrib[
               "fqdn"] == "stationnameoverridemodifiedoverride.standalone.radio.ebu.io"
    assert xml_root.find(".//{http://www.worlddab.org/schemas/spi/31}radiodns").attrib[
               "serviceIdentifier"] == "ebu2standalone"

    genres = xml_root.findall(".//{http://www.worlddab.org/schemas/spi/31}genre")
    assert len(genres) == 3
    assert genres[0].attrib["href"] == "urn:tva:metadata:cs:ContentCS:2011:3.1.1.13"
    assert genres[0].text == "Weather forecasts"
    assert genres[1].attrib["href"] == "urn:tva:metadata:cs:ContentCS:2011:3.1.1.16"
    assert genres[1].text == "Current Affairs"
    assert genres[2].attrib["href"] == "urn:tva:metadata:cs:ContentCS:2011:3.6.4"
    assert genres[2].text == "Pop-rock"
