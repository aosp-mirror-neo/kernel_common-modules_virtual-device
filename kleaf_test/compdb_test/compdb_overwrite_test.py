# Copyright (C) 2026 The Android Open Source Project
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
import subprocess
import sys

def load_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=pathlib.Path)
    return parser.parse_known_args()

arguments = argparse.Namespace()

class CompdbOverwriteTest(unittest.TestCase):
    def _verify_module_config(
        self, tmp_dir, mod_name, expected_config, unexpected_config
    ):
        headers = list(
            pathlib.Path(tmp_dir).glob(
                f"**/{mod_name}/"
                "compile_commands_common_out_dir/**/autoconf.h"
            )
        )
        self.assertEqual(
            len(headers),
            1,
            f"Expected exactly 1 autoconf.h for {mod_name}, "
            f"found {headers}",
        )
        content = headers[0].read_text()
        self.assertIn(
            expected_config,
            content,
            f"{expected_config} not found in {mod_name} autoconf.h",
        )
        self.assertNotIn(
            unexpected_config,
            content,
            f"{unexpected_config} found in {mod_name} autoconf.h",
        )

    def test_no_overwrite(self):
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

            self._verify_module_config(
                tmp_dir,
                "overwrite_mod_a",
                "CONFIG_OVERWRITE_MOD_A",
                "CONFIG_OVERWRITE_MOD_B",
            )
            self._verify_module_config(
                tmp_dir,
                "overwrite_mod_b",
                "CONFIG_OVERWRITE_MOD_B",
                "CONFIG_OVERWRITE_MOD_A",
            )

if __name__ == "__main__":
    arguments, unknown = load_arguments()
    sys.argv[1:] = unknown
    absltest.main()
