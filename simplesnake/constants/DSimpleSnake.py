from typing import Final


class DSimpleSnake:
    VERSION: Final[str] = "0.3.0"
    CMDB_TYPE: Final[str] = "application"
    CMDB_SUBTYPE: Final[str] = "Application"
    CMDB_SUPPLIER: Final[str] = "Nadim-Daniel"
    CMDB_CODENAME: Final[str] = "Xanthosoma"
    CMDB_COMPONENTS = (("localization", "simplesnake/interface/Localizer.py"),)
    CMDB_DATABASES = ()
    CMDB_NETWORK: Final[tuple] = ()
    BASE_DIR: Final[str] = "/opt/prod/simplesnake"
    APPLICATION_ID: Final[str] = "SimpleSnake"
    ORGANIZATION: Final[str] = "BMForge"
    MODEL_FILE: Final[str] = "models/best-model.pth"
    DEFAULT_LOCALE: Final[str] = "en"
