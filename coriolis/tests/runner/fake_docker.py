from enum import Enum

# Classes for mocking docker behaviour

class DockerAction(Enum):
    CREATE_CLIENT = 1
    CREATE_CONTAINER = 2
    RUN_CONTAINER = 3
    START_CONTAINER = 4
    RELOAD_CONTAINER = 5
    STOP_CONTAINER = 6

class DockerActionList:
    actions = []

    @staticmethod
    def add_action(action):
        DockerActionList.actions.append(action)

    @staticmethod
    def get_actions():
        return DockerActionList.actions

    @staticmethod
    def clean_actions():
        DockerActionList.actions = []


class FakeDockerContainer:
    def __init__(self, image):
        self.id = "Fake container id"
        self.image = image

    def stop(self):
        DockerActionList.add_action((DockerAction.STOP_CONTAINER, self.image))

    def reload(self):
        DockerActionList.add_action((DockerAction.RELOAD_CONTAINER, self.image))
        return self


class FakeDockerContainers:
    def create(self, image, **kwargs):
        DockerActionList.add_action((DockerAction.CREATE_CONTAINER, image))
        return FakeDockerContainer(image)

    def run(self, image, **kwargs):
        DockerActionList.add_action((DockerAction.RUN_CONTAINER, image))
        return FakeDockerContainer(image)


class FakeDockerClient:
    def __init__(self):
        self.api = "Fake Docker API"
        self.containers = FakeDockerContainers()


class FakeDockerModule:
    def from_env(self):
        DockerActionList.add_action(DockerAction.CREATE_CLIENT)
        return FakeDockerClient()


class FakeDockerPtyModule:
    def start(self, docker_client, docker_container):
        DockerActionList.add_action(DockerAction.START_CONTAINER)