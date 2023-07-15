import docker
from termcolor import colored


def container_is_healthy(name_or_id: str):
    return docker.from_env().api.inspect_container(name_or_id)["State"]["Status"] == 'running'


def color_text(text: str, color: str, bold: bool = False):
    return colored(text, color, attrs=[] if not bold else ["bold"])