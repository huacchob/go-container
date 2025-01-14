import os
import typing as t

from yaml import dump, safe_load

from utils import (
    find_file_path,
    get_secret,
    load_secrets_from_file,
)

creds_env_file: str = find_file_path(
    target_file_name="creds.env",
    source_file_name=__file__,
)
docker_compose_file: str = find_file_path(
    target_file_name="docker-compose.yml", source_file_name=__file__
)

load_secrets_from_file(target_file_name="creds.env", source_file_name=__file__)


def get_secrets_from_file(file: str) -> t.List[str]:
    """Get secrets.

    Args:
        file (str): The environment file

    Returns:
        t.List[str]: List of secrets.
    """
    with open(file=file, mode="r", encoding="utf-8") as creds_file:
        creds_file: t.TextIO
        secrets_values: str = creds_file.read()
        secrets_values_list: t.List[str] = secrets_values.split(sep="\n")

    secrets: t.List[str] = []

    for secret_pair in secrets_values_list:
        if secret_pair.startswith("#"):
            continue
        split_secret: t.List[str] = secret_pair.split(sep="=")
        if os.environ.get(split_secret[0], default=None):
            secrets.append(split_secret[0])
    return secrets


secrets: t.List[str] = get_secrets_from_file(file=creds_env_file)


def get_docker_secrets(
    file: str,
) -> t.Tuple[t.Dict[t.Any, t.Any], t.List[str]]:
    """Get docker secrets.

    Args:
        file (str): The docker compose file.

    Returns:
        t.Tuple[t.Dict[t.Any, t.Any], t.List[str]]:
            Docker compose config and secrets.
    """
    with open(
        file=file,
        mode="r",
        encoding="utf-8",
    ) as docker_compose_file_read:
        docker_compose_config: t.Dict[
            str, t.Dict[str, t.Dict[str, t.Union[str, t.List[str]]]]
        ] = safe_load(stream=docker_compose_file_read)

    go_secrets_path: t.Union[str, t.List[str]] = (
        docker_compose_config.get(
            "services",
            {},
        )
        .get(
            "go-app",
            {},
        )
        .get(
            "environment",
            [],
        )
    )

    total_secrets: t.List[str] = []

    if go_secrets_path:
        total_secrets.extend(go_secrets_path)

    return docker_compose_config, total_secrets


docker_compose_config, total_secrets = get_docker_secrets(
    file=docker_compose_file,
)


def write_secrets_to_docker_compose(
    docker_compose_config: t.Dict[t.Any, t.Any],
    total_secrets: t.List[str],
    file: str,
) -> None:
    """Write secrets to docker compose.

    Args:
        docker_compose_config (t.Dict[t.Any, t.Any]):
            Docker compose config object.
        total_secrets (t.List[str]): List of secrets.
        file (str): The docker compose file.

    Raises:
        ValueError: Secret `secret_name` not found.
    """
    go_secrets: t.List[str] = []

    for secret in total_secrets:
        docker_secret_value: t.List[str] = secret.split(sep="=")
        secret_name: str = docker_secret_value[0]
        if secret_name not in secrets:
            raise ValueError(
                f"Secret {secret_name} not found in creds.env file",
            )
        secret_value: str = get_secret(secret_name=secret_name)
        if secret_name.startswith("GITHUB"):
            go_secrets.append(f"{secret_name}={secret_value}")

    docker_compose_config.get(
        "services",
        {},
    ).get(
        "go-app",
        {},
    )["environment"] = go_secrets

    with open(
        file=file,
        mode="w",
        encoding="utf-8",
    ) as docker_compose_file_write:
        docker_compose_file_write: t.TextIO
        dump(data=docker_compose_config, stream=docker_compose_file_write)


write_secrets_to_docker_compose(
    docker_compose_config=docker_compose_config,
    total_secrets=total_secrets,
    file=docker_compose_file,
)
