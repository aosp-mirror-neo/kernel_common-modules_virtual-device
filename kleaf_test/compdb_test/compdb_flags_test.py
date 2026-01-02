# Copyright (C) 2025 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from absl.testing import absltest
import argparse
import json
import pathlib
import unittest
import tempfile
import shlex
import subprocess
import sys


def load_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=pathlib.Path)
    return parser.parse_known_args()


arguments = argparse.Namespace()


class CompdbFlagsTest(unittest.TestCase):
    def test_config_matches(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_json = pathlib.Path(tmp_dir) / "compile_commands.json"
            subprocess.check_call(
                [
                    arguments.target,
                    "--out_directory",
                    tmp_dir,
                    str(tmp_json)
                ],
            stdout=subprocess.DEVNULL)
            content = json.loads(tmp_json.read_text())

            for item in content:
                with self.subTest(file=item["file"]):
                    self._check_flags_exist(item)

    def _check_flags_exist(self, item):
        directory = pathlib.Path(item["directory"])
        command_tokens = shlex.split(item["command"])
        flag_files = [token.removeprefix("@")
                      for token in command_tokens if token.startswith("@")]
        for flag_file in flag_files:
            flag_file_real = directory / flag_file
            self.assertTrue(flag_file_real.exists(),
                            f"{flag_file_real} does not exist")
            self.assertFalse("COMMON_OUT_DIR" in flag_file_real.read_text())
            self.assertFalse("ROOT_DIR" in flag_file_real.read_text())


if __name__ == "__main__":
    arguments, unknown = load_arguments()
    sys.argv[1:] = unknown
    absltest.main()
