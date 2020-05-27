from django.db import models

from apps.manager.models import Organization


LANGUAGE_CHOICES = [
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
    ("zh-TW", "正體中文(繁體"),
]


class Station(models.Model):
    name = models.CharField(max_length=80)
    short_name = models.CharField(max_length=8)
    medium_name = models.CharField(max_length=16)
    long_name = models.CharField(max_length=128)
    short_description = models.CharField(max_length=180)
    long_description = models.CharField(max_length=1200)
    url_default = models.URLField()

    postal_name = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=25)
    phone_number = models.CharField(max_length=128)
    sms_number = models.CharField(max_length=128)
    sms_body = models.CharField(max_length=255)
    sms_description = models.CharField(max_length=255)
    email_address = models.EmailField()
    email_description = models.CharField(max_length=255)
    keywords = models.CharField(max_length=255)

    default_language = models.CharField(
        max_length=5, choices=LANGUAGE_CHOICES, default="en"
    )

    location_country = models.CharField(
        max_length=5, choices=LANGUAGE_CHOICES, default="en"
    )

    radiovis_enabled = models.BooleanField()
    radiovis_service = models.CharField(max_length=255)
    radioepg_enabled = models.BooleanField()
    radioepgpi_enabled = models.BooleanField(default=False)
    radioepg_service = models.CharField(max_length=255)
    radiotag_enabled = models.BooleanField(default=False)
    radiotag_service = models.CharField(max_length=255)
    radiospi_enabled = models.BooleanField()
    radiospi_service = models.CharField(max_length=255)

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    ip_allowed = models.CharField(max_length=256)  # A list of ip/subnet, with , between
    genres = models.TextField()


class GenericServiceFollowingEntry(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, null=True)
    # TODO POSSIBLY INCLUDE CHANNEL
    active = models.BooleanField()
    cost = models.IntegerField()
    offset = models.IntegerField()
    mime_type = models.CharField(max_length=255)
    bitrate = models.IntegerField()
