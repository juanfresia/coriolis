import unittest
import os
from tests.runner.fake_docker import *
from unittest.mock import patch

from runner.runner_cli import Runner
from common.utils import *

@patch('runner.runner_cli.docker', new=FakeDockerModule())
@patch('runner.runner_cli.dockerpty', new=FakeDockerPtyModule())
class TestRunnerMethods(unittest.TestCase):
    checkpoints_file = "resources/h2o.chk"
    source_folder = "../examples/h2o/"
    destination_folder = "/tmp/coriolis_runner_test/"

    def test_runner_creates_docker_client(self):
        DockerActionList.clean_actions()
        r = Runner("py", self.checkpoints_file)
        all_docker_actions = DockerActionList.get_actions()
        self.assertIn(DockerAction.CREATE_CLIENT, all_docker_actions)

    def test_runner_instruments_file(self):
        DockerActionList.clean_actions()
        r = Runner("py", self.checkpoints_file)
        r.instrument(self.source_folder)
        instrumented_code_path = r._get_instrumented_code_dir()
        self.assertTrue(os.path.isdir(instrumented_code_path))
        self.assertTrue(os.path.isfile(instrumented_code_path + "run_coriolis.sh"))
        r.clean_tmp_dir()

    def test_runner_runs_detached_container(self):
        DockerActionList.clean_actions()
        r = Runner("py", self.checkpoints_file)
        image = language_to_docker_image("py")
        r.instrument(self.source_folder)
        r.run_code(self.destination_folder, 1, 1.5)

        all_docker_actions = DockerActionList.get_actions()
        self.assertIn( (DockerAction.RUN_CONTAINER, image), all_docker_actions)
        self.assertIn( (DockerAction.STOP_CONTAINER, image), all_docker_actions)
        r.clean_tmp_dir()

    def test_runner_runs_interactive_container(self):
        DockerActionList.clean_actions()
        r = Runner("py", self.checkpoints_file)
        image = language_to_docker_image("py")
        r.instrument(self.source_folder)
        r.run_code(self.destination_folder, 1, 0)

        all_docker_actions = DockerActionList.get_actions()
        self.assertIn( (DockerAction.CREATE_CONTAINER, image), all_docker_actions)
        self.assertIn(DockerAction.START_CONTAINER, all_docker_actions)
        r.clean_tmp_dir()