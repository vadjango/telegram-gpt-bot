import gettext
from config import LANG

GETTEXT_DOMAIN = "gptbot"
GETTEXT_DIR = "locales"

translate: dict[str, gettext.GNUTranslations] = {
    loc: gettext.GNUTranslations(open(gettext.find(GETTEXT_DOMAIN, GETTEXT_DIR, languages=[loc]), "rb"))
    for loc in LANG.values()
}

if __name__ == "__main__":
    print(translate)

