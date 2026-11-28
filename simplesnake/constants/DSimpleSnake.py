from typing import Final


class DSimpleSnake:
    # Release and installation tools read these literal values without importing us.
    VERSION: Final[str] = "0.4.3"
    CMDB_TYPE: Final[str] = "application"
    CMDB_SUBTYPE: Final[str] = "Application"
    CMDB_SUPPLIER: Final[str] = "Nadim-Daniel"
    CMDB_CODENAME: Final[str] = "Hebbian"
    CMDB_COMPONENTS = (("localization", "simplesnake/interface/Localizer.py"),)
    CMDB_DATABASES = ()
    CMDB_NETWORK: Final[tuple] = ()
    BASE_DIR: Final[str] = "/opt/prod/simplesnake"
    APPLICATION_ID: Final[str] = "SimpleSnake"
    ORGANIZATION: Final[str] = "BMForge"
    MODEL_FILE: Final[str] = "models/best-model.pth"
    DEFAULT_LOCALE: Final[str] = "en"
