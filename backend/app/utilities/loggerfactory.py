import yaml
import os
import logging
import logging.config
from app.configs.settings import Directories


class LoggerFactory(object):
    """
    This class generates Logger objects from the base logging module and configures them
    based on a single config file so creating loggers can be done in one line more easily.

    Example:
        ::

            from backend.utilities.loggerfactory import LoggerFactory

            verbose = 'INFO' # ['INFO', 'ERROR', 'DEBUG']
            _logger = LoggerFactory.getLogger("root", log_level=verbose)
            _logger.info("Test Message")

    Attributes:
        _LOGGER (logging): A quick temp object to help return generated loggers

    """

    _LOGGER = None

    @staticmethod
    def __create_logger(name, log_level):
        """
        Helper function to generate a logger based on the configuration files.
        """
        
        with open(os.path.join(Directories.CONF_DIRECTORY, 'logging.conf'), 'r') as stream:
            log_configs = yaml.load(stream, Loader=yaml.FullLoader)

        logging.config.dictConfig(log_configs)
        LoggerFactory._LOGGER = logging.getLogger(name)

        if log_level == 'INFO':
            LoggerFactory._LOGGER.setLevel(logging.INFO)
        elif log_level == 'ERROR':
            LoggerFactory._LOGGER.setLevel(logging.ERROR)
        elif log_level == 'DEBUG':
            LoggerFactory._LOGGER.setLevel(logging.DEBUG)
        return LoggerFactory._LOGGER

    @staticmethod
    def getLogger(name, log_level='DEBUG'):
        """

        Args:
            name (str): This is the name of the logger in the config.
            log_level (str): Currently the supported levels are 'INFO', 'ERROR' and 'DEBUG'

        Returns:
            _LOGGER (logging)

        """
        if name in logging.Logger.manager.loggerDict.keys():
            return logging.getLogger(name)
        else:
            return LoggerFactory.__create_logger(name, log_level)
