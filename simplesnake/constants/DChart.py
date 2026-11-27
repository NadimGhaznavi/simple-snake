from typing import Final


class DChart:
    PLOTLY_VERSION: Final[str] = "4.1.1"
    PLOTLY_FILE: Final[str] = "plotly-4.1.1.min.js"
    ASSET_DIRECTORY: Final[str] = "assets"
    PAGE_FILE: Final[str] = "training-chart.html"
    SCRIPT_FILE: Final[str] = "training-chart.js"
    READY_TIMEOUT_MS: Final[int] = 15000
