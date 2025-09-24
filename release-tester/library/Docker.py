import docker
import sys
from library import Log
from pathlib import Path
import platform
from dotenv import dotenv_values

LOGGER = Log.Log()


##
# Docker
##
def get_platform():
    os_name = platform.system()
    arch = platform.machine()

    if os_name == "Darwin" and arch == "arm64":
        return "linux/amd64"

    # Default fallback
    return None

def get_client():
    try:
        docker_client = docker.from_env()
        docker_client.ping()
        return docker_client
    except docker.errors.DockerException as e:
        LOGGER.error(f"Error connecting to Docker:{os.linesep} {e}")
        sys.exit(1)


def create_container(
    image_name,
    container_name,
    container_command=None,
    container_link=None,
    container_volumes=None,
    environment_variables=None,
    ports=None,
    detach=False,
    extra_hosts=None,
    network=None,
    env_file_path=None
):
    """
    Creates a Docker container, optionally loading environment variables from a .env file.
    Explicitly passed environment_variables override .env values.
    """
    docker_client = get_client()

    # Avoid mutable default args
    container_volumes = container_volumes or {}
    environment_variables = environment_variables or {}
    ports = ports or {}
    extra_hosts = extra_hosts or {}

    # Load .env file if provided
    if env_file_path:
        env_path = Path(env_file_path)
        if env_path.exists():
            file_envs = dotenv_values(env_path)
            # Merge, giving priority to explicitly passed env vars
            merged_envs = {**file_envs, **environment_variables}
            environment_variables = merged_envs
        else:
            LOGGER.warning(f".env file not found at {env_file_path}")
  
    kwargs={
        "image":image_name,
        "name":container_name,
        "environment":environment_variables,
        "ports":ports,
        "command":container_command,
        "links":container_link,
        "volumes":container_volumes,
        "detach":detach,
        "extra_hosts":extra_hosts
    }
    platform=get_platform()
    if platform:
        kwargs["platform"]=platform

    # Check if image exists locally
    docker_images = docker_client.images.list()
    image_exists = any(image_name in image.tags for image in docker_images)

    if not image_exists:
        tmp_args={
            "repository":image_name,
        }
        if platform:
            tmp_args["platform"]=platform
            LOGGER.info("Docker - create_container",f"Pulling {image_name} (Platform: {platform})...")
        else:
            LOGGER.info("Docker - create_container",f"Pulling {image_name}...")
        docker_client.images.pull(**tmp_args)
        LOGGER.info("Docker - create_container",f"Successfully pulled {image_name}!")

    # Create container
    container = docker_client.containers.create(
        **kwargs
    )

    # Attach to network if specified
    if network:
        net = docker_client.networks.get(network)
        net.connect(container)

    return container


def run_command_in_container(container_name="", command_to_run=""):
    """
    Runs the given command inside the container using the exec function.

    :param container_name: Name of container
    :param command_to_run: Command to run (String)
    """
    client = docker.from_env()
    target_container = client.containers.get(container_name)

    command_status, command_output = target_container.exec_run(
        command_to_run, stderr=True, stdout=True, tty=False
    )

    return (command_status, command_output)
