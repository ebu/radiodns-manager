import json
from functools import reduce

from fixtures.raw_data_channel import channels
from fixtures.raw_data_channel_pictures import channel_pictures
from fixtures.raw_data_client import clients
from fixtures.raw_data_epg_shows import epg_shows
from fixtures.raw_data_event import events
from fixtures.raw_data_generic_service_following_entry import generic_service_following_entry
from fixtures.raw_data_organization import organizations
from fixtures.raw_data_station import stations
from fixtures.raw_logo_image import logo_images

# ============================================================================================
# LOCALIZATION
# ============================================================================================
COUNTRIES_N_CODES = list(map(lambda e: e[1] + (e[0]+1,), enumerate([
    ("1", "9E0", "al", "Albania (AL)"),
    ("2", "2E0", "dz", "Algeria (DZ)"),
    ("3", "2E0", "dz", "Algeria (DZ)"),
    ("4", "3E0", "ad", "Andorra (AD)"),
    ("5", "6D0", "ao", "Angola (AO)"),
    ("6", "1A2", "ai", "Anguilla (AI)"),
    ("7", "2A2", "ag", "Antigua and Barbuda (AG)"),
    ("8", "AA2", "ar", "Argentina (AR)"),
    ("9", "AE4", "am", "Armenia (AM)"),
    ("10", "3A4", "aw", "Aruba (AW)"),
    ("11", "1F0", "au", "Australia - Australian Capital Territory (AU)"),
    ("12", "2F0", "au", "Australia - New South Wales (AU)"),
    ("13", "8F0", "au", "Australia - Northern Territory (AU)"),
    ("14", "4F0", "au", "Australia - Queensland (AU)"),
    ("15", "5F0", "au", "Australia - South Australia (AU)"),
    ("16", "7F0", "au", "Australia - Tasmania (AU)"),
    ("17", "3F0", "au", "Australia - Victoria (AU)"),
    ("18", "6F0", "au", "Australia - Western Australia (AU)"),
    ("19", "AE0", "at", "Austria (AT)"),
    ("20", "BE3", "az", "Azerbaijan (AZ)"),
    ("21", "8E4", "pt", "Azores Portugal (PT)"),
    ("22", "FA2", "bs", "Bahamas (BS)"),
    ("23", "EF0", "bh", "Bahrain (BH)"),
    ("24", "3F1", "bd", "Bangladesh (BD)"),
    ("25", "5A2", "bb", "Barbados (BB)"),
    ("26", "FE3", "by", "Belarus (BY)"),
    ("27", "FE3", "by", "Belarus (BY)"),
    ("28", "6E0", "be", "Belgium (BE)"),
    ("29", "6A2", "bz", "Belize (BZ)"),
    ("30", "ED0", "bj", "Benin (BJ)"),
    ("31", "CA2", "bm", "Bermuda (BM)"),
    ("32", "2F1", "bt", "Bhutan (BT)"),
    ("33", "1A3", "bo", "Bolivia (BO)"),
    ("34", "FE4", "ba", "Bosnia-Herzegovina (BA)"),
    ("35", "BD1", "bw", "Botswana (BW)"),
    ("36", "BA2", "br", "Brazil (BR)"),
    ("37", "BF1", "bn", "Brunei Darussalam (BN)"),
    ("38", "8E1", "bg", "Bulgaria (BG)"),
    ("39", "BD0", "bf", "Burkina Faso (BF)"),
    ("40", "9D1", "bi", "Burundi (BI)"),
    ("41", "3F2", "kh", "Cambodia (KH)"),
    ("42", "1D0", "cm", "Cameroon (CM)"),
    ("43", "BA1", "ca", "Canada B (CA)"),
    ("44", "CA1", "ca", "Canada C (CA)"),
    ("45", "DA1", "ca", "Canada D (CA)"),
    ("46", "EA1", "ca", "Canada E (CA)"),
    ("47", "EE2", "es", "Canaries Spain (ES)"),
    ("48", "EE0", "es", "Canary Islands Spain (ES)"),
    ("49", "6D1", "cv", "Cape Verde (CV)"),
    ("50", "7A2", "ky", "Cayman Islands (KY)"),
    ("51", "2D0", "cf", "Central African Republic (CF)"),
    ("52", "9D2", "td", "Chad (TD)"),
    ("53", "CA3", "cl", "Chile (CL)"),
    ("54", "CF0", "cn", "China (CN)"),
    ("55", "2A3", "co", "Colombia (CO)"),
    ("56", "CD1", "km", "Comoros (KM)"),
    ("57", "CD0", "cg", "Congo (CG)"),
    ("58", "8A2", "cr", "Costa Rica (CR)"),
    ("59", "CD2", "ci", "Cote d.Ivoire (CI)"),
    ("60", "CE3", "hr", "Croatia (HR)"),
    ("61", "9A2", "cu", "Cuba (CU)"),
    ("62", "2E1", "cy", "Cyprus (CY)"),
    ("63", "2E2", "cz", "Czech Republic (CZ)"),
    ("64", "BD2", "zr", "Democratic Rep. of Congo (ZR)"),
    ("65", "9E1", "dk", "Denmark (DK)"),
    ("66", "3D0", "dj", "Djibouti (DJ)"),
    ("67", "AA3", "dm", "Dominica (DM)"),
    ("68", "BA3", "do", "Dominican Republic (DO)"),
    ("69", "3A2", "ec", "Ecuador (EC)"),
    ("70", "FE0", "eg", "Egypt (EG)"),
    ("71", "FE0", "eg", "Egypt (EG)"),
    ("72", "CA4", "sv", "El Salvador (SV)"),
    ("73", "7D0", "gq", "Equatorial Guinea (GQ)"),
    ("74", "2E4", "ee", "Estonia (EE)"),
    ("75", "2E4", "ee", "Estonia (EE)"),
    ("76", "ED1", "et", "Ethiopia (ET)"),
    ("77", "4A2", "fk", "Falkland Islands (FK)"),
    ("78", "9E1", "dk", "Faroe Islands Denmark (DK)"),
    ("79", "5F1", "fj", "Fiji (FJ)"),
    ("80", "6E1", "fi", "Finland (FI)"),
    ("81", "FE1", "fr", "France (FR)"),
    ("82", "8D0", "ga", "Gabon (GA)"),
    ("83", "8D1", "gm", "Gambia (GM)"),
    ("84", "CE4", "ge", "Georgia (GE)"),
    ("85", "1E0", "de", "Germany 1 (DE)"),
    ("86", "DE0", "de", "Germany D (DE)"),
    ("87", "3D1", "gh", "Ghana (GH)"),
    ("88", "AE1", "gi", "Gibraltar United Kingdom (GI)"),
    ("89", "1E1", "gr", "Greece (GR)"),
    ("90", "FA1", "gl", "Greenland (GL)"),
    ("91", "DA3", "gd", "Grenada (GD)"),
    ("92", "EA2", "gp", "Guadeloupe (GP)"),
    ("93", "1A4", "gt", "Guatemala (GT)"),
    ("94", "5A3", "gf", "Guiana (GF)"),
    ("95", "AD2", "gw", "Guinea-Bissau (GW)"),
    ("96", "FA3", "gy", "Guyana (GY)"),
    ("97", "DA4", "ht", "Haiti (HT)"),
    ("98", "2A4", "hn", "Honduras (HN)"),
    ("99", "FF1", "hk", "Hong Kong (HK)"),
    ("100", "BE0", "hu", "Hungary (HU)"),
    ("101", "AE2", "is", "Iceland (IS)"),
    ("102", "5F2", "in", "India (IN)"),
    ("103", "CF2", "id", "Indonesia (ID)"),
    ("104", "8F0", "ir", "Iran (IR)"),
    ("105", "BE1", "iq", "Iraq (IQ)"),
    ("106", "BE1", "iq", "Iraq (IQ)"),
    ("107", "2E3", "ie", "Ireland (IE)"),
    ("108", "4E0", "il", "Israel (IL)"),
    ("109", "5E0", "it", "Italy (IT)"),
    ("110", "3A3", "jm", "Jamaica (JM)"),
    ("111", "9F2", "jp", "Japan (JP)"),
    ("112", "5E1", "jo", "Jordan (JO)"),
    ("113", "DE3", "kz", "Kazakhstan (KZ)"),
    ("114", "6D2", "ke", "Kenya (KE)"),
    ("115", "1F1", "ki", "Kiribati (KI)"),
    ("116", "DF0", "kp", "Korea North (KP)"),
    ("117", "EF1", "kr", "Korea South (KR)"),
    ("118", "1F2", "kw", "Kuwait (KW)"),
    ("119", "3E4", "kg", "Kyrgyzstan (KG)"),
    ("120", "1F3", "la", "Laos (LA)"),
    ("121", "9E3", "lv", "Latvia (LV)"),
    ("122", "9E3", "lv", "Latvia (LV)"),
    ("123", "AE3", "lb", "Lebanon (LB)"),
    ("124", "6D3", "ls", "Lesotho (LS)"),
    ("125", "2D1", "lr", "Liberia (LR)"),
    ("126", "DE1", "ly", "Libya (LY)"),
    ("127", "DE1", "ly", "Libya (LY)"),
    ("128", "9E2", "li", "Liechtenstein (LI)"),
    ("130", "CE2", "lt", "Lithuania (LT)"),
    ("129", "CE2", "lt", "Lithuania (LT)"),
    ("131", "7E1", "lu", "Luxembourg (LU)"),
    ("132", "6F2", "mo", "Macau (MO)"),
    ("133", "4E3", "mk", "Macedonia (MK)"),
    ("134", "4D0", "mg", "Madagascar (MG)"),
    ("135", "8E4", "pt", "Madeira Portugal (PT)"),
    ("136", "FD0", "mw", "Malawi (MW)"),
    ("137", "FF0", "my", "Malaysia (MY)"),
    ("138", "BF2", "mv", "Maldives (MV)"),
    ("139", "5D0", "ml", "Mali (ML)"),
    ("140", "CE0", "mt", "Malta (MT)"),
    ("141", "4A3", "mq", "Martinique (MQ)"),
    ("142", "4D1", "mr", "Mauritania (MR)"),
    ("143", "AD3", "mu", "Mauritius (MU)"),
    ("144", "BA5", "mx", "Mexico B (MX)"),
    ("145", "DA5", "mx", "Mexico D (MX)"),
    ("146", "EA5", "mx", "Mexico E (MX)"),
    ("147", "FA5", "mx", "Mexico F (MX)"),
    ("148", "EF3", "fm", "Micronesia (FM)"),
    ("149", "1E4", "md", "Moldova (MD)"),
    ("150", "1E4", "md", "Moldova (MD)"),
    ("151", "BE2", "mc", "Monaco (MC)"),
    ("152", "FF3", "mn", "Mongolia (MN)"),
    ("153", "5A4", "ms", "Montserrat (MS)"),
    ("154", "1E2", "ma", "Morocco (MA)"),
    ("155", "1E2", "ma", "Morocco (MA)"),
    ("156", "3D2", "mz", "Mozambique (MZ)"),
    ("157", "BF0", "mm", "Myanmar Burma (MM)"),
    ("158", "1D1", "na", "Namibia (NA)"),
    ("159", "7F1", "nr", "Nauru (NR)"),
    ("160", "EF2", "np", "Nepal (NP)"),
    ("161", "8E3", "nl", "Netherlands (NL)"),
    ("162", "DA2", "an", "Netherlands Antilles (AN)"),
    ("163", "9F1", "nz", "New Zealand (NZ)"),
    ("164", "7A3", "ni", "Nicaragua (NI)"),
    ("165", "8D2", "ne", "Niger (NE)"),
    ("166", "FD1", "ng", "Nigeria (NG)"),
    ("167", "FE2", "no", "Norway (NO)"),
    ("168", "6F1", "om", "Oman (OM)"),
    ("169", "4F1", "pk", "Pakistan (PK)"),
    ("170", "8E0", "ps", "Palestine (PS)"),
    ("171", "9A3", "a", "Panama (A)"),
    ("172", "9F3", "pg", "Papua New Guinea (PG)"),
    ("173", "6A3", "py", "Paraguay (PY)"),
    ("174", "7A4", "pe", "Peru (PE)"),
    ("175", "8F2", "ph", "Philippines (PH)"),
    ("176", "3E2", "pl", "Poland (PL)"),
    ("177", "8E4", "pt", "Portugal (PT)"),
    ("191", "2F2", "qa", "Qatar (QA)"),
    ("192", "9D0", "gn", "Republic of Guinea (GN)"),
    ("193", "EE1", "ro", "Romania (RO)"),
    ("194", "7E0", "ru", "Russian Federation (RU)"),
    ("195", "7E0", "ru", "Russian Federation (RU)"),
    ("196", "5D3", "rw", "Rwanda (RW)"),
    ("197", "AA4", "kn", "Saint Kitts (KN)"),
    ("198", "BA4", "lc", "Saint Lucia (LC)"),
    ("199", "CA5", "vc", "Saint Vincent (VC)"),
    ("200", "3E1", "sm", "San Marino (SM)"),
    ("201", "5D1", "st", "Sao Tome &amp; Principe (ST)"),
    ("202", "9F0", "sa", "Saudi Arabia (SA)"),
    ("203", "7D1", "sn", "Senegal (SN)"),
    ("204", "8D3", "sc", "Seychelles (SC)"),
    ("205", "1D2", "sl", "Sierra Leone (SL)"),
    ("206", "AF2", "sg", "Singapore (SG)"),
    ("207", "5E2", "sk", "Slovakia (SK)"),
    ("208", "9E4", "si", "Slovenia (SI)"),
    ("209", "AF1", "sb", "Solomon Islands (SB)"),
    ("210", "7D2", "so", "Somalia (SO)"),
    ("211", "AD0", "za", "South Africa (ZA)"),
    ("212", "EE2", "es", "Spain (ES)"),
    ("213", "CF1", "lk", "Sri Lanka (LK)"),
    ("214", "FA6", "pm", "St Pierre and Miquelon (PM)"),
    ("215", "CD3", "sd", "Sudan (SD)"),
    ("216", "8A4", "sr", "Suriname (SR)"),
    ("217", "5D2", "sz", "Swaziland (SZ)"),
    ("218", "EE3", "se", "Sweden (SE)"),
    ("219", "4E1", "ch", "Switzerland (CH)"),
    ("220", "6E2", "sy", "Syrian Arab Republic (SY)"),
    ("221", "DF1", "tw", "Taiwan (TW)"),
    ("222", "5E3", "tj", "Tajikistan (TJ)"),
    ("223", "DD1", "tz", "Tanzania (TZ)"),
    ("224", "2F3", "th", "Thailand (TH)"),
    ("225", "DD0", "tg", "Togo (TG)"),
    ("226", "3F3", "to", "Tonga (TO)"),
    ("227", "6A4", "tt", "Trinidad and Tobago (TT)"),
    ("228", "7E2", "tn", "Tunisia (TN)"),
    ("229", "7E2", "tn", "Tunisia (TN)"),
    ("230", "3E3", "tr", "Turkey (TR)"),
    ("231", "EE4", "tm", "Turkmenistan (TM)"),
    ("232", "EA3", "tc", "Turks and Caicos Islands (TC)"),
    ("233", "DF2", "ae", "UAE (AE)"),
    ("234", "4D2", "ug", "Uganda (UG)"),
    ("235", "6E4", "ua", "Ukraine (UA)"),
    ("236", "6E4", "ua", "Ukraine (UA)"),
    ("237", "CE1", "gb", "United Kingdom (GB)"),
    ("238", "1A0", "us", "United States of America 1 (US)"),
    ("239", "2A0", "us", "United States of America 2 (US)"),
    ("240", "3A0", "us", "United States of America 3 (US)"),
    ("241", "4A0", "us", "United States of America 4 (US)"),
    ("242", "5A0", "us", "United States of America 5 (US)"),
    ("243", "6A0", "us", "United States of America 6 (US)"),
    ("244", "7A0", "us", "United States of America 7 (US)"),
    ("245", "8A0", "us", "United States of America 8 (US)"),
    ("246", "9A0", "us", "United States of America 9 (US)"),
    ("247", "AA0", "us", "United States of America A (US)"),
    ("248", "BA0", "us", "United States of America B (US)"),
    ("249", "DA0", "us", "United States of America D (US)"),
    ("250", "EA0", "us", "United States of America E (US)"),
    ("251", "9A4", "uy", "Uruguay (UY)"),
    ("252", "BE4", "uz", "Uzbekistan (UZ)"),
    ("253", "FF2", "vu", "Vanuatu (VU)"),
    ("254", "4E2", "va", "Vatican City State (VA)"),
    ("255", "EA4", "ve", "Venezuela (VE)"),
    ("256", "7F2", "vn", "Vietnam (VN)"),
    ("257", "FA5", "vg", "Virgin Islands British (VG)"),
    ("271", "3D3", "eh", "Western Sahara (EH)"),
    ("272", "4F2", "ws", "Western Samoa (WS)"),
    ("273", "BF3", "ye", "Yemen (YE)"),
    ("274", "DE2", "yu", "Yugoslavia (YU)"),
    ("275", "ED2", "zm", "Zambia (ZM)"),
    ("276", "2D2", "zw", "Zimbabwe (ZW)"),
])))

LANGUAGES = list(map(lambda e: e[1] + (e[0]+1,), enumerate([
    ("af", "Afrikaans"),
    ("ak", "Akan"),
    ("an", "aragonés"),
    ("ar", "عربي"),
    ("as", "অসমীয়া"),
    ("ast", "Asturianu"),
    ("az", "Azərbaycanca"),
    ("be", "Беларуская"),
    ("bg", "Български"),
    ("br", "Brezhoneg"),
    ("ca", "Català"),
    ("cs", "Čeština"),
    ("csb", "Kaszëbsczi"),
    ("cy", "Cymraeg"),
    ("da", "Dansk"),
    ("de", "Deutsch"),
    ("dsb", "Dolnoserbšćina"),
    ("el", "Ελληνικά"),
    ("en-GB", "English(British)"),
    ("en-US", "English(US)"),
    ("eo", "Esperanto"),
    ("es-AR", "Español(de Argentina)"),
    ("es-CL", "Español(de Chile)"),
    ("es-ES", "Español(de España)"),
    ("es-MX", "Español(de México)"),
    ("et", "Eesti keel"),
    ("eu", "Euskara"),
    ("fa", "فارسی"),
    ("ff", "Pulaar - Fulfulde"),
    ("fi", "suomi"),
    ("fr", "Français"),
    ("fy-NL", "Frysk"),
    ("ga-IE", "Gaeilge"),
    ("gd", "Gàidhlig"),
    ("gl", "Galego"),
    ("he", "עברית"),
    ("hi-IN", "हिन्दी(भारत)"),
    ("hr", "Hrvatski"),
    ("hsb", "Hornjoserbsce"),
    ("hu", "magyar"),
    ("hy-AM", "Հայերեն"),
    ("id", "Bahasa Indonesia"),
    ("is", "íslenska"),
    ("it", "Italiano"),
    ("ja", "日本語"),
    ("ka", "ქართული"),
    ("kk", "Қазақ"),
    ("km", "ខ្មែរ"),
    ("ko", "한국어"),
    ("ku", "Kurdî"),
    ("lg", "Luganda"),
    ("lij", "Ligure"),
    ("lt", "lietuvių kalba"),
    ("lv", "Latviešu"),
    ("mk", "Македонски"),
    ("ml", "മലയാളം"),
    ("mr", "मराठी"),
    ("ms", "Melayu"),
    ("my", "မြန်မာဘာသာ"),
    ("nb-NO", "Norsk bokmål"),
    ("nl", "Nederlands"),
    ("nso", "Sepedi"),
    ("oc", "occitan(lengadocian)"),
    ("pa-IN", "ਪੰਜਾਬੀ(ਭਾਰਤ)"),
    ("pl", "Polski"),
    ("pt-BR", "Português(do Brasil)"),
    ("pt-PT", "Português(Europeu)"),
    ("rm", "rumantsch"),
    ("ro", "română"),
    ("ru", "Русский"),
    ("sk", "slovenčina"),
    ("sl", "Slovenščina"),
    ("son", "Soŋay"),
    ("sq", "Shqip"),
    ("sr", "Српски"),
    ("sv-SE", "Svenska"),
    ("ta", "தமிழ்"),
    ("te", "తెలుగు"),
    ("th", "ไทย"),
    ("tr", "Türkçe"),
    ("uk", "Українська"),
    ("ur", "اُردو"),
    ("vi", "Tiếng Việt"),
    ("xh", "isiXhosa"),
    ("zh-CN", "中文(简体)"),
    ("zh-TW", "正體中文(繁體)"),
])))


def pk_to_set(acc, v):
    acc.add(v["pk"])
    return acc


def reduce_by_iso(acc, v):
    acc[v[2]] = v
    return acc


def reduce_by_code(acc, v):
    acc[v[0]] = v
    return acc


ecc_by_iso = reduce(lambda acc, v: reduce_by_iso(acc, v), COUNTRIES_N_CODES, {})
lang_by_code = reduce(lambda acc, v: reduce_by_code(acc, v), LANGUAGES, {})

# ============================================================================================
# ORGANIZATION (Service provider)
# ============================================================================================
new_organizations = []
for organization in organizations:
    new_organizations.append({
        "model": "manager.Organization",
        "pk": organization[0],
        "fields": {
            "codops": organization[1],
            "short_name": organization[2],
            "medium_name": organization[3],
            "long_name": organization[4],
            "short_description": organization[5],
            "long_description": organization[6],
            "url_default": organization[7],
            "postal_name": organization[14],
            "street": organization[15],
            "city": organization[11],
            "zipcode": organization[16],
            "phone_number": organization[13],
            "default_language": lang_by_code[organization[8]][2] if organization[8] in lang_by_code else None,  # ForeignKey
            "location_country": ecc_by_iso[organization[9]][4] if organization[9] in ecc_by_iso else None,  # ForeignKey
            "default_image_id": organization[10],
        }
    })

with open('json_fixtures/new_organizations.json', 'w') as fp:
    json.dump(new_organizations, fp, indent=4, sort_keys=True)

# ============================================================================================
# LOGO IMAGE
# ============================================================================================

existing_orgas = reduce(pk_to_set, new_organizations, set())
new_logo_images = []
for logo_image in logo_images:
    if logo_image[8] not in existing_orgas:
        print(logo_image[8], "isn't a valid org. Skipping...")
        continue
    new_logo_images.append({
        "model": "manager.LogoImage",
        "pk": logo_image[0],
        "fields": {
            "organization": logo_image[8],
            "name": logo_image[10],
            "file": logo_image[2],
            "scaled32x32": logo_image[3],
            "scaled112x32": logo_image[4],
            "scaled128x128": logo_image[5],
            "scaled320x240": logo_image[6],
            "scaled600x600": logo_image[7],
        }
    })

with open('json_fixtures/new_logo_images.json', 'w') as fp:
    json.dump(new_logo_images, fp, indent=4, sort_keys=True)

# ============================================================================================
# CHANNEL PICTURE
# ============================================================================================


def orga_tuple_to_set(acc, v):
    acc[v[1]] = v[8]
    return acc


sp_to_orga_mapping = reduce(orga_tuple_to_set, logo_images, {})

new_channel_pictures = []
for picture in channel_pictures:
    if picture[1] not in existing_orgas:
        print(picture[1], "isn't a valid org. Skipping...")
        continue
    new_channel_pictures.append({
        "model": "channels.Image",
        "pk": picture[0],
        "fields": {
            "organization": sp_to_orga_mapping[picture[1]],
            "name": picture[2],
            "file": picture[3],
            "radiotext": picture[4],
            "radiolink": picture[5],
        }
    })

existing_channel_pictures = reduce(pk_to_set, new_channel_pictures, set())

with open('json_fixtures/new_channel_pictures.json', 'w') as fp:
    json.dump(new_channel_pictures, fp, indent=4, sort_keys=True)

# ============================================================================================
# CLIENT
# ============================================================================================
new_clients = []
for client in clients:
    if client[2] not in existing_orgas:
        print(client[2], "isn't a valid org. Skipping...")
        continue
    new_clients.append({
        "model": "clients.Client",
        "pk": client[0],
        "fields": {
            "name": client[1],
            "organization": sp_to_orga_mapping[client[2]],
            "identifier": client[3],
            "email": client[4],
        }
    })

with open('json_fixtures/new_clients.json', 'w') as fp:
    json.dump(new_clients, fp, indent=4, sort_keys=True)

# ============================================================================================
# STATIONS
# ============================================================================================
new_stations = []
new_station_instances = []
for index, station in enumerate(stations):

    if station[1] not in existing_orgas:
        print(station[1], "isn't a valid org. Skipping...")
        continue

    new_stations.append({
        "model": "stations.Station",
        "pk": station[0],
        "fields": {
            "organization": station[8],  # ForeignKey
            "default_image": station[15],  # ForeignKey
            "radiovis_enabled": station[13] if station[13] is not None else False,
            "radiovis_service": station[14],
            "radioepg_enabled": station[9] if station[9] is not None else False,
            "radioepgpi_enabled": station[33] if station[33] is not None else False,
            "radioepg_service": station[10],
            "radiotag_enabled": station[11] if station[11] is not None else False,
            "radiotag_service": station[12],
            "radiospi_enabled": station[34] if station[34] is not None else False,
            "radiospi_service": station[35],
            "ip_allowed": station[4],
        }
    })

    new_station_instances.append({
        "model": "stations.StationInstance",
        "fields": {
            "station": station[0],  # ForeignKey
            "name": station[2],
            "short_name": station[5],
            "medium_name": station[18],
            "long_name": station[17],
            "short_description": station[6],
            "url_default": station[19],
            "postal_name": station[25],
            "street": station[29],
            "city": station[20],
            "zipcode": station[30],
            "phone_number": station[24],
            "sms_number": station[28],
            "sms_body": station[26],
            "sms_description": station[27],
            "email_address": station[31],
            "email_description": station[32],
            "default_language": lang_by_code[station[21]][2] if station[21] in lang_by_code else None,  # ForeignKey
            "location_country": ecc_by_iso[station[23]][4] if station[23] in ecc_by_iso else None,  # ForeignKey
            "genres": station[7],
            "client": station[37],
        }
    })

existing_stations = reduce(pk_to_set, new_stations, set())

with open('json_fixtures/new_stations.json', 'w') as fp:
    json.dump(new_stations, fp, indent=4, sort_keys=True)

with open('json_fixtures/new_station_instances.json', 'w') as fp:
    json.dump(new_station_instances, fp, indent=4, sort_keys=True)

# ============================================================================================
# CHANNELS
# ============================================================================================
new_channels = []
for channel in channels:
    if channel[16] not in existing_channel_pictures:
        print(channel[16], "isn't a channel picture. Skipping...")
        continue
    if channel[1] not in existing_stations:
        print(channel[1], "isn't a station. Skipping...")
        continue

    new_channels.append({
        "model": "channels.Channel",
        "pk": channel[0],
        "fields": {
            "station": channel[1],  # ForeignKey
            "name": channel[2],
            "appty_uatype": channel[3],
            "ecc": channel[5],  # ForeignKey
            "eid": channel[6],
            "fqdn": channel[7],
            "frequency": channel[8],
            "pa": channel[9],
            "pi": channel[10],
            "scids": channel[11],
            "serviceIdentifier": channel[12],
            "sid": channel[13],
            "tx": channel[14],
            "type_id": channel[15],
            "default_image": channel[16],  # ForeignKey
            "bitrate": channel[17],
            "mime_type": channel[18],
            "stream_url": channel[19],
            "mid": None,
        }
    })

with open('json_fixtures/new_channels.json', 'w') as fp:
    json.dump(new_channels, fp, indent=4, sort_keys=True)

existing_channels = reduce(pk_to_set, new_channels, set())

# ============================================================================================
# EPG - SHOWS
# ============================================================================================

new_shows = []
for show in epg_shows:
    if show[6] is None:
        print("A show must be attached to a station. Skipping...")
        continue
    new_shows.append({
        "model": "radioepg.Show",
        "pk": show[0],
        "fields": {
            "station": show[6],
            "medium_name": show[2],
            "long_name": show[3],
            "description": show[4],
            "color": show[5],
        }
    })

with open('json_fixtures/new_shows.json', 'w') as fp:
    json.dump(new_shows, fp, indent=4, sort_keys=True)

# ============================================================================================
# EPG - EVENT
# ============================================================================================

existing_shows = reduce(pk_to_set, new_shows, set())

new_events = []
for event in events:
    if event[1] not in existing_shows:
        print(event[1], "isn't a show. Skipping...")
        continue
    new_events.append({
        "model": "radioepg.Event",
        "pk": event[0],
        "fields": {
            "day": event[3],
            "start_hour": event[4],
            "start_minute": event[5],
            "length": event[6],
            "show": event[1],
        }
    })

with open('json_fixtures/new_events.json', 'w') as fp:
    json.dump(new_events, fp, indent=4, sort_keys=True)

# ============================================================================================
# EPG - generic service following entry
# ============================================================================================

new_generic_service_following_entry = []
for entry in generic_service_following_entry:
    if entry[5] not in existing_stations and entry[5] is not None:
        print(entry[5], "isn't a station. Skipping...")
        continue
    if entry[4] not in existing_channels and entry[4] is not None:
        print(entry[4], "isn't a channel. Skipping...")
        continue
    new_generic_service_following_entry.append({
        "model": "radioepg.GenericServiceFollowingEntry",
        "pk": entry[0],
        "fields": {
            "station": entry[5],
            "channel": entry[4],
            "active": entry[1],
            "cost": entry[2],
            "offset": entry[3],
            "mime_type": entry[7],
            "bitrate": entry[8],
        }
    })

with open('json_fixtures/new_generic_service_following_entry.json', 'w') as fp:
    json.dump(new_generic_service_following_entry, fp, indent=4, sort_keys=True)
