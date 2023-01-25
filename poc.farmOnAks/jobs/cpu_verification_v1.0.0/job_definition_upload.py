#!/usr/bin/env python3

import argparse

from dataclasses import (
    asdict,
    dataclass,
    field,
)
from typing import (
    Dict,
    Optional,
)

try:
    import requests
except ImportError:
    raise Exception("'requests' python package is required, install and try again. 'pip install requests'")

try:
    import toml
except ImportError:
    raise Exception("'toml' python package is required, install and try again. 'pip install toml'")


@dataclass
class _JobDefinition:
    name: str
    job_type: str
    command: str
    job_spec_path: Optional[str] = None
    args: list = field(default_factory=list)
    task_function: Optional[str] = None
    env: Dict = field(default_factory=dict)
    log_to_stdout: Optional[bool] = True
    extension_paths: list = field(default_factory=list)
    allowed_args: Dict = field(default_factory=dict)
    headless: Optional[bool] = True
    active: Optional[bool] = True
    unresolved_command_path: Optional[str] = None
    success_return_codes: list = field(default_factory=lambda: [0])
    capacity_requirements: Dict = field(default_factory=dict)
    working_directory: Optional[str] = ""
    container: Optional[str] = None


def _load_job_definitions(job_config_filepath: str, force: bool = False):
    job_config = toml.load(job_config_filepath)
    jobs = job_config.get("job")
    if not jobs:
        raise Exception(f"No job definitions found in config file: {job_config_filepath}")

    job_definitions = []
    for job_name, params in jobs.items():
        if not params.get("container"):
            print(f"WARNING: There is no container defined for '{job_name}'.")

        if "unresolved_command_path" not in params:
            params["unresolved_command_path"] = params["command"]

        if "job_spec_path" not in params:
            params["job_spec_path"] = str(job_config_filepath)

        try:
            job_definition = _JobDefinition(**params)
        except TypeError as exc:
            raise Exception(f"Error processing job definition '{job_name}'. {exc}") from exc

        job_definitions.append(job_definition)

    return job_definitions


def upload_job_definitions(farm_url, job_definitions_file, api_key, timeout):
    jobs_save_endpoint = f"{farm_url.rstrip('/')}/queue/management/jobs/save"
    job_defs = _load_job_definitions(job_definitions_file)
    print(f"Found '{len(job_defs)}' Job definition(s) in '{job_definitions_file}'")

    for job in job_defs:
        print(f"\nUploading Job definition: '{job.name}'")
        response = requests.post(
            url=jobs_save_endpoint,
            json=asdict(job),
            timeout=timeout,
            headers={"X-API-KEY": api_key},
        )
        response.raise_for_status()
        print(f'Response: {response.json()}')


def main():
    parser = argparse.ArgumentParser(description="Upload and save job definitions found in the job config")

    parser.add_argument('job_definitions_file', help="TOML file containing the Job definitions.")
    parser.add_argument('--farm-url', help="Farm base URL.", required=True)
    parser.add_argument('--api-key', help="Jobs API Key.", required=True)
    parser.add_argument('--timeout', type=int, default=60, help="Request timeout.")

    args = parser.parse_args()

    upload_job_definitions(args.farm_url, args.job_definitions_file, args.api_key, args.timeout)


if __name__ == '__main__':
    main()
