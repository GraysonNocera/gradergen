import tomllib
import zipfile
import pathlib
from typing import Callable

class Generator:
    def __init__(self, path_to_config: str) -> None:
        self.path_to_config = pathlib.Path(path_to_config).resolve()

        with open(path_to_config, "rb") as f:
            self.config = tomllib.load(f)

        zip_file = self.config.get("zip_file", f"{self.config["executable"]}.zip")
        self.zip = zipfile.ZipFile(zip_file, "w")

    def generate(self) -> None:
        path_to_inputs = pathlib.Path(self.config["tests"].get("input_directory", "inputs"))
        path_to_expected = pathlib.Path(self.config["tests"].get("expected_directory", "expected"))

        for file in path_to_inputs.glob("*"):
            file = pathlib.Path(file.parts[-1])
            self.zip.write(path_to_inputs / file, path_to_inputs.parts[-1] / file)

        for file in path_to_expected.glob("*"):
            file = pathlib.Path(file.parts[-1])
            self.zip.write(path_to_expected / file, path_to_expected.parts[-1] / file)

        self._generate_template_file(self.config, "setup-sh", "setup.sh")
        self._generate_template_file(self.config, "requirements-txt", "requirements.txt")
        self._generate_template_file(self.config, "run_tests-py", "run_tests.py")
        self._generate_template_file(self.config, "run_autograder", "run_autograder")

        self._generate_tests()

        path_to_tests = pathlib.Path(__file__).parent / "templates" / "tests"

        path_to_weights = path_to_tests / "weights.py"
        self.zip.write(path_to_weights, pathlib.Path(path_to_tests.parts[-1]) / "weights.py")

        path_to_config_parser = path_to_tests / "config.py" 
        self.zip.write(path_to_config_parser, pathlib.Path(path_to_tests.parts[-1]) / "config.py")

        self.zip.write(self.path_to_config, pathlib.Path(path_to_tests.parts[-1]) / self.path_to_config.parts[-1])

        for file in self.config.get("extra_files", []):
            self.zip.write(file, pathlib.Path(file).parts[-1])

        self.zip.close()

    def _generate_tests(self) -> None:
        config = self.config["tests"]
        path_to_tests = pathlib.Path("tests")
        self._generate_template_file(config, "test_files", path_to_tests / "test_files.py")
        self._generate_template_file(config, "test_compile", path_to_tests / "test_compile.py")
        self._generate_template_file(config, "test_program", path_to_tests / "test_program.py")

    def _generate_template_file(self, base_config: dict, key: str, default_filename: str) -> None:
        config = base_config.get(key, {})
        if "path" in config and config["path"]:
            self.zip.write(config["path"], default_filename)
            return
        path_to_template = pathlib.Path(__file__).parent / "templates" / default_filename
        self.zip.write(path_to_template, default_filename)
