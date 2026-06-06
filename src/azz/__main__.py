from .app import main
from .logging import configure_logging

if __name__ == "__main__":
    configure_logging()
    main()
