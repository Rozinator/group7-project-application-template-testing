import os
import json
import tempfile
import shutil
import unittest
from types import SimpleNamespace
import config


class TestConfig(unittest.TestCase):

    def setUp(self):
        # Reset config state
        config._config = None
        for env in ["TEST_PARAM_X", "MISSING_PARAM", "ANYTHING_NOT_HERE"]:
            if env in os.environ:
                del os.environ[env]

    # ---------------------------
    # convert_to_typed_value tests
    # ---------------------------

    def test_convert_json_string(self):
        val = '{"a": 1, "b": [1,2]}'
        out = config.convert_to_typed_value(val)
        self.assertEqual(out["a"], 1)
        self.assertEqual(out["b"], [1, 2])

    def test_convert_invalid_json_returns_string(self):
        out = config.convert_to_typed_value("not-json{")
        self.assertEqual(out, "not-json{")

    def test_convert_none(self):
        self.assertIsNone(config.convert_to_typed_value(None))

    # ---------------------------
    # set/get parameter tests
    # ---------------------------

    def test_set_parameter_string(self):
        config.set_parameter("TEST_PARAM_X", "hello")
        self.assertEqual(config.get_parameter("TEST_PARAM_X"), "hello")

    def test_set_parameter_json(self):
        config.set_parameter("TEST_PARAM_X", {"num": 10})
        out = config.get_parameter("TEST_PARAM_X")
        self.assertEqual(out["num"], 10)

    def test_get_parameter_default_value(self):
        self.assertEqual(config.get_parameter("MISSING_PARAM", default="fallback"), "fallback")

    def test_get_parameter_not_found(self):
        self.assertIsNone(config.get_parameter("NOT_PRESENT_AT_ALL"))

    # ---------------------------
    # overwrite_from_args
    # ---------------------------

    def test_overwrite_from_args(self):
        args = SimpleNamespace(x=5, y="hello", user=None)
        config.overwrite_from_args(args)
        self.assertEqual(config.get_parameter("x"), 5)
        self.assertEqual(config.get_parameter("y"), "hello")

    # ---------------------------
    # _init_config + _get_default_path
    # ---------------------------

    def test_init_config_loads_file(self):
        tmpdir = tempfile.mkdtemp()
        prev = os.getcwd()
        try:
            os.chdir(tmpdir)
            with open("config.json", "w") as f:
                f.write(json.dumps({"TESTNUM": 777}))

            config._config = None
            config._init_config()

            self.assertEqual(config.get_parameter("TESTNUM"), 777)
        finally:
            os.chdir(prev)
            shutil.rmtree(tmpdir)

    def test_init_config_no_file(self):
        tmpdir = tempfile.mkdtemp()
        prev = os.getcwd()
        try:
            os.chdir(tmpdir)
            config._config = None
            config._init_config()

            out = config.get_parameter("ANYTHING_NOT_HERE")
            self.assertIsNone(out)
        finally:
            os.chdir(prev)
            shutil.rmtree(tmpdir)


if __name__ == "__main__":
    unittest.main()
