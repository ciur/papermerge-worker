import yaml
import os
import logging
import logging.config

ENG = "eng"
DEU = "deu"


def lang_human_name(lang):
    lang_map = {
        'eng': 'English',
        'deu': 'Deutsch'
    }

    if lang in lang_map.keys():
        return lang_map[lang]

    return False


logger = logging.getLogger(__name__)


def setup_logging():
    """
    Load logging configuration from a logging.yml.
    It will search for file in:
        * current dir
        * /etc/briolette dir

    If none of the files was found, skip silently loging setup.
    Because it is either not important or perfomed in different
    place (in django settings)
    """
    config_file_name = "logging.yml"
    etc_config_file_path = "/etc/briolette/{}".format(config_file_name)
    config_file_path = None

    if os.access(config_file_name, os.R_OK):
        config_file_path = config_file_name
    elif os.access(etc_config_file_path, os.R_OK):
        config_file_path = etc_config_file_path

    if config_file_path:
        with open(config_file_path, "r") as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)

