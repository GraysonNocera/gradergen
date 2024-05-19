import unittest
from gradescope_utils.autograder_utils.decorators import weight
import os
import test_compile
import test_files
import weights
import subprocess
from config import config
from parameterized import parameterized

NUM_TESTS = sum(1 for value in config.get("tests", {}).get("test_program", {}).values() if isinstance(value, dict)) 

class test_program(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        test_files.test_files().test_files()
        test_compile.test_compile().test_compile()

        self._base_directory = os.path.dirname(os.path.dirname(__file__))

        input_directory_name = config.get("tests", {}).get("input_directory", "inputs")    
        self._input_directory = os.path.join(self._base_directory, input_directory_name)
        self._input_files = os.listdir(self._input_directory)

        expected_directory_name = config.get("tests", {}).get("expected_directory", "expected")
        self._expected_directory = os.path.join(self._base_directory, expected_directory_name)
        self._expected_files = os.listdir(self._expected_directory)


    def load_test_cases(self):
        test_cases = []
        config_tests = config.get("tests", {}).get("test_program", {})
        for key in config_tests:
            if isinstance(config_tests[key], dict):
                command_arguments = config_tests[key].get("command_arguments", "")
                expected_output = config_tests[key].get("expected_output", "")
                output = config_tests[key].get("output", "stdout")

                test_cases.append((key, command_arguments, output, expected_output))

        return test_cases
    
    @weight(weights.TEST_PROGRAM / NUM_TESTS)
    @parameterized.expand(load_test_cases)
    def test_program(self, _, command_arguments, output, expected_output):
        
        executable = config.get("global", {}).get("executable", "a.out")
        command = f"./{executable} {' '.join(command_arguments)}"
        process = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))

        if output == "stdout":
            result = process.stdout
        else:
            result = open(output, "r").read()
          
        try: # TODO: there must be a better way of doing this
            expected = open(expected_output, "r").read()
        except:
            expected = expected_output

        if result != expected:
            self.print_difference(result, expected)
            self.assertTrue(False)

        self.assertTrue(True)
    
    def print_different(self, result, expected): 
        result_split = set(result.split("\n"))
        expected_split = set(expected.split("\n"))
        missing_from_output = expected_split.difference(result_split)
        missing_from_output = "\n".join(missing_from_output)
        extra_from_output = result_split.difference(expected_split)
        extra_from_output = "\n".join(extra_from_output)
        print("RESULTS\n")
        print("Lines missing from your output (NOT NECESSARILY IN THIS ORDER):")
        print("-----START-----")
        print(missing_from_output)
        print("----- END -----\n")
        print("Extra lines from your output (NOT NECESSARILY IN THIS ORDER):")
        print("-----START-----")
        print(extra_from_output)
        print("----- END -----")