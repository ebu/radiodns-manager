import pytest
import requests
from sqlalchemy import text

from tests.conftest import TEST_PROXY_URL, TEST_RADIO_DNS_URL
import xml.etree.ElementTree as ET
from tests.utilities.utilities import compare_lists, sql_alchemy_result_to_list

MYSQL_SERVICE_PROVIDER_QUERY = "SELECT codops, short_name, medium_name, long_name, short_description" \
                               ", url_default, default_language, location_country, " \
                               "city, phone_number, postal_name, street, zipcode FROM service_provider WHERE id = 1"

SERVICE_PROVIDER_HTML_TR = [
    "CODOPS standalone",
    "Short Name EBU",
    "Medium Name European BU",
    "Long Name European Broadcasting Union",
    "Short Description THE EUROPEAN BROADCASTING UNION IS THE WORLD’S LEADING ALLIANCE OF PUBLIC SERVICE MEDIA",
    "Default Url https://github.com/ebu",
    "Default Language en-GB",
    "Postal Address EBU\nL'Ancienne-Route 17A\nLe Grand-Saconnex, 1218",
    "Country France",
    "Phone Number 022 717 21 11",
]

SERVICE_PROVIDER_MYSQL_TR = [
    "standalone",
    "EBU",
    "European BU",
    "European Broadcasting Union",
    "THE EUROPEAN BROADCASTING UNION IS THE WORLD’S LEADING ALLIANCE OF PUBLIC SERVICE MEDIA",
    "https://github.com/ebu",
    "en-GB",
    "fr",
    "Le Grand-Saconnex",
    "022 717 21 11",
    "EBU",
    "L'Ancienne-Route 17A",
    "1218"
]


@pytest.mark.run(order=1)
def test_no_provider(stack_setup, browser_setup):
    driver = browser_setup
    driver.get(TEST_PROXY_URL + "serviceprovider/images/")
    assert len(driver.find_elements_by_class_name("alert-warning")) == 1

    driver.get(TEST_PROXY_URL + "radioepg/logos/")
    assert len(driver.find_elements_by_class_name("alert-warning")) == 1

    driver.get(TEST_PROXY_URL + "radioepg/servicefollowing/")
    assert len(driver.find_elements_by_class_name("alert-warning")) == 1

    driver.get(TEST_PROXY_URL + "radioepg/schedule/")
    assert len(driver.find_elements_by_class_name("alert-warning")) == 1


@pytest.mark.run(order=2)
def test_create_service_provider(stack_setup, browser_setup):
    db = stack_setup
    driver = browser_setup
    driver.get(TEST_PROXY_URL + "serviceprovider/edit/-")

    # Is page loaded?
    assert ":: PlugIt -Standalone mode" == driver.title

    # Fill inputs
    driver.find_element_by_name("short_name").send_keys("EBU")
    driver.find_element_by_name("medium_name").send_keys("European BU")
    driver.find_element_by_name("long_name").send_keys("European Broadcasting Union")
    driver.find_element_by_name("short_description").send_keys(
        "THE EUROPEAN BROADCASTING UNION IS THE WORLD’S LEADING ALLIANCE OF PUBLIC SERVICE MEDIA")
    driver.find_element_by_name("default_language").find_element_by_css_selector("option[value=en-GB]").click()
    driver.find_element_by_name("url_default").send_keys("https://github.com/ebu")
    driver.find_element_by_name("postal_name").send_keys("EBU")
    driver.find_element_by_name("street").send_keys("L'Ancienne-Route 17A")
    driver.find_element_by_name("zipcode").send_keys("1218")
    driver.find_element_by_name("city").send_keys("Le Grand-Saconnex")
    driver.find_element_by_name("location_country").find_element_by_css_selector("option[value=fr]").click()
    driver.find_element_by_name("phone_number").send_keys("022 717 21 11")
    driver.find_element_by_css_selector("input[type=submit][value=Save]").click()

    # Check entered data
    tr_list = list(map(lambda x: x.text, driver
                       .find_element_by_class_name("table-responsive")
                       .find_elements_by_css_selector("tr")))
    assert compare_lists(tr_list, SERVICE_PROVIDER_HTML_TR)

    # Check db
    result = db.engine.execute(text(MYSQL_SERVICE_PROVIDER_QUERY))
    assert result.rowcount == 1
    assert compare_lists(sql_alchemy_result_to_list(result)[0], SERVICE_PROVIDER_MYSQL_TR, True)

    # Check XML
    res = requests.get(TEST_RADIO_DNS_URL + "radiodns/spi/3.1/SI.xml")
    assert res.status_code == 200
    attrib_root = ET.fromstring(res.text).attrib
    assert "originator" in attrib_root
    assert attrib_root["originator"] == "EBU.io RadioDNS Services v3"
