import os
import logging
import subprocess
import json
import shutil
from pprint import pformat
from json.decoder import JSONDecodeError

EXIFTOOL_CMD = 'exiftool'


class UnsupportedFileTypeExcetion(Exception):
    pass


class ExifToolBackend(object):
    def __init__(self,
                 metadata_fields,
                 tag_prefix,
                 exec_cmd=EXIFTOOL_CMD,
                 exiftool_config_path=None,
                 stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE,
                 overwrite_original=False):

        self._metadata_fields_map = {field['id']: field for field in metadata_fields}
        self.tag_prefix = tag_prefix
        self.exec_cmd = exec_cmd
        self.exiftool_config_path = exiftool_config_path
        self.stdout = stdout
        self.stderr = stderr
        self.overwrite_original = overwrite_original

        self.open()

    def open(self):
        self._is_open = True

    def stop(self):
        self._is_open = False

    def close(self):
        self.stop()

    def __enter__(self):
        self.open()

    def __exit__(self):
        self.close()

    def _make_cmd(self, *args):
        config_args  = () if self.exiftool_config_path is None else ('-config', self.exiftool_config_path)
        cmd = (self.exec_cmd,) + config_args + args
        logging.debug('exiftool command:\n{}\n'.format(' '.join(cmd)))
        return cmd

    def execute_standalone(self, *args):
        return subprocess.run(self._make_cmd(*args), stdout=self.stdout, stderr=self.stderr)

    def execute(self, *args):
        return self.execute_standalone(*args)

    def cmdfy_tag(self, tag):
        if self.tag_prefix is not None:
            return '-{}{}'.format(self.tag_prefix, tag) \
                if not tag.startswith(self.tag_prefix) \
                else '-{}'.format(tag)
        else:
            return '-{}'.format(tag)

    def get_tags(self, *files):
        try:
            metadata = json.loads(self.execute('-json', self.cmdfy_tag('*'), *files).stdout)
        except JSONDecodeError as e:
            logging.debug('JSONDecodeError: {}'.format(str(e)))
            return {f: {} for f in files}

        filtered = {}
        for tags in metadata:
            if 'SourceFile' in tags:
                filtered[tags['SourceFile']] = {}
                for k, v in tags.items():
                    if k != 'SourceFile':
                        filtered[tags['SourceFile']][k.lower()] = v

        for f in files:
            if f not in filtered:
                filtered[f] = {}
        return filtered

    def set_tags(self, *args, **metadata):
        exec_args = args + tuple([
            "{}={}".format(self.cmdfy_tag(tag), val)
            for tag, val in metadata.items()
        ])

        if self.overwrite_original:
            exec_args += ('-overwrite_original', )

        outcome = self.execute(*exec_args)
        logging.debug('\nStdout: {}'.format(outcome.stdout))
        logging.debug('\nStderr: {}'.format(outcome.stderr))

    def copy(self, src_fp, dest_fp):
        if not os.path.exists(src_fp):
            raise ValueError('Source file does not exist.')
        elif not os.path.exists(os.path.dirname(dest_fp)):
            os.makedirs(os.path.dirname(dest_fp))

        shutil.copy2(src_fp, dest_fp)

    def move(self, src_fp, dest_fp):
        if not os.path.exists(src_fp):
            raise ValueError('Source file does not exist.')
        elif not os.path.exists(os.path.dirname(dest_fp)):
            os.makedirs(os.path.dirname(dest_fp))

        shutil.move(src_fp, dest_fp)

    def remove(self, *files):
        for f in files:
            os.remove(f)

if __name__ == '__main__':
    print('This module is only for importing into other modules.')
