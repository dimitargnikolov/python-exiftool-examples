import sys
import os
import time
import random
import logging
import unittest
import shutil
import json
import string
from datetime import datetime
from pprint import pformat

from backend_test import BackendTest
from exiftool_backend import ExifToolBackend

logging.basicConfig(level=logging.DEBUG)

class TestExifToolBackend(unittest.TestCase, BackendTest):

    EXIF_CONFIG_FILE = 'custom.config'
    METADATA_SCHEMA_FILE = 'metadata-schema.json'

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)

        with open(self.METADATA_SCHEMA_FILE, 'r') as f:
            metadata_fields = json.loads(f.read())['fields']

        BackendTest.__init__(
            self,
            metadata_fields,
            ExifToolBackend(
                metadata_fields,
                'XMP-rt:',
                exiftool_config_path=self.EXIF_CONFIG_FILE,
                overwrite_original=True
            )
        )

    def _create_copy(self, filepath):
        newpath = '{}.{}'.format(filepath, time.time())
        shutil.copy(filepath, newpath)
        return newpath

    def setUp(self):
        logging.debug('Copying f1.')
        self.f1 = self._create_copy(self.f1)

        logging.debug('Copying f2.')
        self.f2 = self._create_copy(self.f2)

    def tearDown(self):
        logging.debug('Deleting {} and {}'.format(self.f1, self.f2))

        if os.path.exists(self.f1):
            os.remove(self.f1)

        if os.path.exists(self.f2):
            os.remove(self.f2)

        logging.debug('Tear down complete.')

if __name__ == '__main__':
    unittest.main()
