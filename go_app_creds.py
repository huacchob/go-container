import os
import typing as t

from yaml import dump, safe_load

from utils import (
    find_file_path,
    get_secret,
    load_secrets_from_file,
)

creds_env_file: t.Optional[str | None] = find_file_path(
    target_file_name="creds.env",
    source_file_name=__file__,
)
docker_compose_file: t.Optional[str | None] = find_file_path(
    target_file_name="docker-compose.yml", source_file_name=__file__
)

load_secrets_from_file(target_file_name="creds.env", source_file_name=__file__)

if not creds_env_file:
    raise ValueError("creds.env file not found")

with open(file=creds_env_file, mode="r", encoding="utf-8") as creds_file:
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

if not docker_compose_file:
    raise ValueError("docker-compose.yml file not found")

with open(
    file=docker_compose_file,
    mode="r",
    encoding="utf-8",
) as docker_compose_file_read:
    docker_compose_config: t.Dict[
        str, t.Dict[str, t.Dict[str, t.Union[str, t.List[str]]]]
    ] = safe_load(stream=docker_compose_file_read)

go_secrets_path: t.Union[str, t.List[str]] = (
    docker_compose_config.get("services", {}).get("go-app", {}).get("environment", [])
)

total_secrets: t.List[str] = []

if isinstance(go_secrets_path, list):
    total_secrets.extend(go_secrets_path)

go_secrets: t.Sequence[str] = []

for secret in total_secrets:
    docker_secret_value: t.List[str] = secret.split(sep="=")
    secret_name: str = docker_secret_value[0]
    if secret_name not in secrets:
        raise ValueError(f"Secret {secret_name} not found in creds.env file")
    secret_value: str = get_secret(secret_name=secret_name)
    if secret_name.startswith("GITHUB"):
        go_secrets.append(f"{secret_name}={secret_value}")

docker_compose_config.get("services", {}).get("go-app", {})["environment"] = go_secrets

with open(
    file=docker_compose_file, mode="w", encoding="utf-8"
) as docker_compose_file_write:
    docker_compose_file_write: t.TextIO
    dump(data=docker_compose_config, stream=docker_compose_file_write)
