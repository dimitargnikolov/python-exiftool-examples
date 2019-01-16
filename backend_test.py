import os
import time
import random
import json
import logging
import string
from datetime import datetime
from abc import ABC, abstractmethod


class BackendTest(ABC):
    # a directory that may or may not exist on the file system
    # ok not to exist, since the backends don't modify any files
    # just the metadata about them
    TEST_DATA_DIR = 'test-data'

    def __init__(self, metadata_fields, backend):
        self.f1 = '{}/f1.tif'.format(self.TEST_DATA_DIR)
        self.f2 = '{}/f2.tif'.format(self.TEST_DATA_DIR)
        self._metadata_fields_map = {
            field['id']: field for field in metadata_fields
        }
        self.backend = backend

    @abstractmethod
    def setUp(self):
        pass

    @abstractmethod
    def tearDown(self):
        self.backend.close()

    def random_metadata(self):
        metadata = {}

        for field in self._metadata_fields_map:
            assert field not in metadata
            val_type = self._metadata_fields_map[field]['type']

            if val_type == 'enum':
                options = self._metadata_fields_map[field]['options']
                metadata[field] = random.choice(options)['id']
            elif val_type in ['string', 'text']:
                metadata[field] = self.random_string(10)
            elif val_type == 'date':
                # datetimes should only be precise to seconds since
                # some backends might not support higher precision
                metadata[field] = datetime.now().replace(microsecond=0).strftime('%Y-%m-%d-%H%M%S')
            else:
                raise ValueError('Unexpected value in metadata fields structure: {}'.format(field))

        return metadata

    def random_string(self, num_chars):
        alphabet = string.ascii_letters + string.digits
        return ''.join([random.choice(alphabet) for _ in range(num_chars)])

    def test_empty(self):
        all_tags = self.backend.get_tags(self.f1, self.f2)
        self.assertEqual(len(all_tags), 2)
        for uri, tags in all_tags.items():
            self.assertEqual(tags, {})

    def test_random_read_write(self):
        metadata = self.random_metadata()
        r = self.backend.set_tags(self.f1, self.f2, **metadata)

        read_metadata = self.backend.get_tags(self.f1, self.f2)
        logging.debug('read_metadata: {}'.format(read_metadata))
        for filepath in [self.f1, self.f2]:
            self.assertTrue(filepath in read_metadata)
            self.assertEqual(read_metadata[filepath], metadata)

        new_metadata = self.random_metadata()
        self.backend.set_tags(self.f1, **new_metadata)

        read_metadata = self.backend.get_tags(self.f1, self.f2)
        self.assertEqual(new_metadata, read_metadata[self.f1])
        self.assertEqual(metadata, read_metadata[self.f2])

    def test_copy(self):
        src_uri = self.f1
        dest_uri = self.f2
        metadata = self.random_metadata()

        self.backend.set_tags(src_uri, **metadata)
        read_metadata = self.backend.get_tags(src_uri, dest_uri)

        self.assertEqual(read_metadata[src_uri], metadata)
        self.assertEqual(read_metadata[dest_uri], {})

        self.backend.copy(src_uri, dest_uri)
        read_metadata = self.backend.get_tags(src_uri, dest_uri)
        self.assertEqual(read_metadata[src_uri], metadata)
        self.assertEqual(read_metadata[dest_uri], metadata)

    def test_copy_overwrite(self):
        src_uri = self.f1
        dest_uri = self.f2
        src_md = self.random_metadata()
        dest_md = self.random_metadata()

        self.backend.set_tags(src_uri, **src_md)
        self.backend.set_tags(dest_uri, **dest_md)
        read_metadata = self.backend.get_tags(src_uri, dest_uri)
        self.assertEqual(read_metadata[src_uri], src_md)
        self.assertEqual(read_metadata[dest_uri], dest_md)

        self.backend.copy(src_uri, dest_uri)
        read_metadata = self.backend.get_tags(src_uri, dest_uri)
        self.assertEqual(read_metadata[src_uri], src_md)
        self.assertEqual(read_metadata[dest_uri], src_md)

    def test_remove_single(self):
        self.backend.set_tags(self.f1, self.f2, **self.random_metadata())
        read_metadata = self.backend.get_tags(self.f1, self.f2)

        self.assertNotEqual(read_metadata[self.f1], {})
        self.assertNotEqual(read_metadata[self.f2], {})

        self.backend.remove(self.f1)
        read_metadata = self.backend.get_tags(self.f1, self.f2)
        self.assertEqual(read_metadata[self.f1], {})
        self.assertNotEqual(read_metadata[self.f2], {})

        self.backend.remove(self.f2)
        read_metadata = self.backend.get_tags(self.f1, self.f2)
        logging.debug('read_metadata: {}'.format(read_metadata))
        self.assertEqual(read_metadata[self.f1], {})
        self.assertEqual(read_metadata[self.f2], {})

    def test_remove_multiple(self):
        self.backend.set_tags(self.f1, self.f2, **self.random_metadata())
        read_metadata = self.backend.get_tags(self.f1, self.f2)

        self.assertNotEqual(read_metadata[self.f1], {})
        self.assertNotEqual(read_metadata[self.f2], {})

        self.backend.remove(self.f1, self.f2)
        read_metadata = self.backend.get_tags(self.f1, self.f2)

        self.assertEqual(read_metadata[self.f1], {})
        self.assertEqual(read_metadata[self.f2], {})

    def test_move(self):
        md = self.random_metadata()

        self.backend.set_tags(self.f1, **md)
        read_metadata = self.backend.get_tags(self.f1, self.f2)

        self.assertEqual(read_metadata[self.f1], md)
        self.assertEqual(read_metadata[self.f2], {})

        self.backend.move(self.f1, self.f2)
        read_metadata = self.backend.get_tags(self.f1, self.f2)

        self.assertEqual(read_metadata[self.f1], {})
        self.assertEqual(read_metadata[self.f2], md)

    def test_move_overwrite(self):
        md1 = self.random_metadata()
        md2 = self.random_metadata()

        self.backend.set_tags(self.f1, **md1)
        self.backend.set_tags(self.f2, **md2)
        read_metadata = self.backend.get_tags(self.f1, self.f2)

        self.assertEqual(read_metadata[self.f1], md1)
        self.assertEqual(read_metadata[self.f2], md2)

        self.backend.move(self.f2, self.f1)
        read_metadata = self.backend.get_tags(self.f1, self.f2)

        self.assertEqual(read_metadata[self.f1], md2)
        self.assertEqual(read_metadata[self.f2], {})


if __name__ == '__main__':
    print('This module is not meant to be excuted by itself.')
