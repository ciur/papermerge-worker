import os
import sys
import argparse
from unittest.loader import TestLoader
from unittest.runner import TextTestRunner

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

test_loader = TestLoader()
test_runner = TextTestRunner()

# Change env variable before accessing briolette module
os.environ['CELERY_CONFIG_MODULE'] = 'briolette.config_test'
# Briolette module MUST be accessed only after changes
# in environment variables
from briolette import setup_logging

setup_logging()

parser = argparse.ArgumentParser()

parser.add_argument(
    '-p',
    '--pattern',
    default='test*py',
    help='Test files pattern.'
)

args = parser.parse_args()

if args.pattern.endswith('py'):
    discovery_pattern = args.pattern
else:
    discovery_pattern = args.pattern + "*"

tests = test_loader.discover(
    start_dir=BASE_DIR,
    pattern=discovery_pattern
)

result = test_runner.run(tests)

if not result.wasSuccessful():
    sys.exit(1)
