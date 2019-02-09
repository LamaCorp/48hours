import logging
from logging.config import dictConfig
import sentry_sdk
import platform
from constants import VERSION, LOGFILE
from pygame import ver as pygame_ver


def init_logger():
    logging_config = dict(
        version=1,
        formatters={
            'f': {
                'format': '%(asctime)s %(name)-20s %(levelname)-8s %(message)s'
            },
        },
        handlers={
            'console': {'class': 'logging.StreamHandler',
                        'formatter': 'f',
                        'level': logging.DEBUG},
            'file': {'class': 'logging.handlers.RotatingFileHandler',
                     'filename': LOGFILE,
                     'maxBytes': 2**24,
                     'backupCount': 4,
                     'encoding': 'utf-8',
                     'formatter': 'f',
                     'level': logging.DEBUG},
        },
        root={
            'handlers': ['console', 'file'],
            'level': logging.DEBUG,
        },
    )
    dictConfig(logging_config)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.info("Root logger initialized")


def init_sentry(send_log=False):
    logger = logging.getLogger(__name__)

    def before_send(event, hint):
        if 'exc_info' in hint:
            exc_type, exc_value, tb = hint['exc_info']
            if isinstance(exc_type, (KeyboardInterrupt)):  # Add exceptions we want to ignore here
                logger.info(f"Ignoring exception {exc_type} and not sending logs to Sentry")
                return None
        return event
    if send_log:
        logger.info("Initializing Sentry")
        sentry_sdk.init(dsn="https://f0af935af4d64f8c8d19b895e4046c4e@sentry.io/1386886",
                        attach_stacktrace=True,
                        with_locals=True,
                        before_send=before_send,
                        server_name="placeholder")
    else:
        logger.info("De-initializing Sentry")
        sentry_sdk.init()


def log_sysinfo():
    logger = logging.getLogger(__name__)
    logger.info(f"Program version: {VERSION}")
    logger.info(f"Pygame version: {pygame_ver}")
    logger.info(f"Interpreter infos:"
                f"Version: {platform.python_version()} "
                f"Compiler: {platform.python_compiler()} "
                f"Build: {platform.python_build()}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"OS uname: "
                f"system={platform.system()}, "
                f"release={platform.release()}, "
                f"version={platform.version()}, "
                f"machine={platform.machine()}, "
                f"processor={platform.processor()}")
    logger.info(f"Architecture: {platform.architecture()}")
