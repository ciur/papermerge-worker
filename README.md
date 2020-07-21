Papermerge Worker
================

pmwroker's main job is OCR processing. It extracts text from pdf, tiff, jpeg and png.
For full project description please see [Papermerge Project](https://github.com/ciur/papermerge)

Requirements
=============

python >= 3.6

pmworker.wrapper uses subprocess.run method, method added in python 3.5.
Also argument of subprocess.run(encoding='utf-8') is used. This argument
was added python 3.6

Dependencies
=============

Depends on celery, tesseract, imagemagick.

Usage:

> export CELERY_CONFIG_MODULE='pmwroker.config'
> celery -A pmworker.celery worker -l info

Run Tests
=============
Run all tests:
    
    python3 ./test/run.py

Run specific test file:

    python3 ./test/run.py -p test_endpoint

Which is same as:

    python3 ./test/run.py -p test_endpoint.py
