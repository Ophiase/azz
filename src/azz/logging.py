import logging


def configure_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] %(levelname)s in %(name)s: %(message)s",
    )
