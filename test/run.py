import os
import sys
import argparse
from unittest.loader import TestLoader
from unittest.runner import TextTestRunner

from pmworker import setup_logging

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

test_loader = TestLoader()
test_runner = TextTestRunner()

os.environ['CELERY_CONFIG_MODULE'] = 'pmworker.config.test'

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
