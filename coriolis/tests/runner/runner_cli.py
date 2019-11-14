import unittest
from tests.runner.fake_docker import *
from unittest.mock import patch

from runner.runner_cli import *
from common.utils import *


class RunnerArgs:
    def __init__(self, language, checkpoints, source, destination, is_interactive=False):
        self.number_runs = 1
        self.timeout = 0 if is_interactive else 1.5
        self.verbose = False
        self.language = [language]
        self.checkpoints = checkpoints
        self.source = source
        self.destination = destination


@patch('runner.runner_cli.docker', new=FakeDockerModule())
@patch('runner.runner_cli.dockerpty', new=FakeDockerPtyModule())
class TestRunnerH2O(unittest.TestCase):
    checkpoints_file = "resources/h2o.chk"
    source_folder = "../examples/h2o/"
    destination_folder = "/tmp/coriolis_runner_test/"
    args = RunnerArgs("py", checkpoints_file, source_folder, destination_folder)

    def test_run_h2o_example(self):
        DockerActionList.clean_actions()
        run_runner(self.args)
        all_docker_actions = DockerActionList.get_actions()
        image = language_to_docker_image("py")
        self.assertIn(DockerAction.CREATE_CLIENT, all_docker_actions)
        self.assertIn( (DockerAction.RUN_CONTAINER, image), all_docker_actions)
        self.assertIn( (DockerAction.STOP_CONTAINER, image), all_docker_actions)


@patch('runner.runner_cli.docker', new=FakeDockerModule())
@patch('runner.runner_cli.dockerpty', new=FakeDockerPtyModule())
class TestRunnerBarber(unittest.TestCase):
    checkpoints_file = "resources/barber.chk"
    source_folder = "../examples/barber/"
    destination_folder = "/tmp/coriolis_runner_test/"
    args = RunnerArgs("rs", checkpoints_file, source_folder, destination_folder)

    def test_run_h2o_example(self):
        DockerActionList.clean_actions()
        run_runner(self.args)
        all_docker_actions = DockerActionList.get_actions()
        image = language_to_docker_image("rs")
        self.assertIn(DockerAction.CREATE_CLIENT, all_docker_actions)
        self.assertIn( (DockerAction.RUN_CONTAINER, image), all_docker_actions)
        self.assertIn( (DockerAction.STOP_CONTAINER, image), all_docker_actions)


@patch('runner.runner_cli.docker', new=FakeDockerModule())
@patch('runner.runner_cli.dockerpty', new=FakeDockerPtyModule())
class TestRunnerSmokers(unittest.TestCase):
    checkpoints_file = "resources/smokers.chk"
    source_folder = "../examples/smokers/"
    destination_folder = "/tmp/coriolis_runner_test/"
    args = RunnerArgs("c", checkpoints_file, source_folder, destination_folder)

    def test_run_h2o_example(self):
        DockerActionList.clean_actions()
        run_runner(self.args)
        all_docker_actions = DockerActionList.get_actions()
        image = language_to_docker_image("c")
        self.assertIn(DockerAction.CREATE_CLIENT, all_docker_actions)
        self.assertIn( (DockerAction.RUN_CONTAINER, image), all_docker_actions)
        self.assertIn( (DockerAction.STOP_CONTAINER, image), all_docker_actions)


if __name__ == '__main__':
    unittest.main(buffer=True)
