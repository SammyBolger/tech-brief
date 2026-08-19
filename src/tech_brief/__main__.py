"""Entry point for `python -m tech_brief`."""

import logging

from tech_brief.config import settings
from tech_brief.digest import main

if __name__ == "__main__":
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    main()
