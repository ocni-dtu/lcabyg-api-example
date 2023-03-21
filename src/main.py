import json
import os
import requests
from pathlib import Path
import base64
from time import sleep


API_URL = 'https://api1.lcabyg.dk'
API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")
DATA_PATH = Path(__file__).parent / "data"
PROJECT_PATH = DATA_PATH / "single_error.json"
PROJECT_OUT_PATH = DATA_PATH / "single_error_out.json"


def main():
    token = get_token()
    #job_ids = get_jobs(token)
    #get_statuses(token, job_ids)
    job_id = create_job(token)
    download_results(token, job_id)


def get_token():
    auth = {"username": API_USERNAME, "password": API_PASSWORD}
    response = requests.post(f"{API_URL}/v2/login", json=auth)
    response.raise_for_status()
    token = response.json()
    return token


def create_job(token: str) -> str:
    lcabyg_project = base64.b64encode(PROJECT_PATH.read_bytes()).decode()
    headers = {'Authorization': f'Bearer {token}'}
    data = {
      "priority": 0,
      "job_target": "lcabyg5+br23",
      "job_target_min_ver": "",
      "job_target_max_ver": "",
      "job_arguments": "",
      "extra_input": "",
      "input_blob": lcabyg_project
    }
    response = requests.post(f"{API_URL}/v2/jobs", json=data, headers=headers)
    response.raise_for_status()

    data = response.json()
    print(f"CREATED JOB: {data['id']}")
    return data.get("id")


def get_jobs(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{API_URL}/v2/jobs", headers=headers)
    response.raise_for_status()

    data = response.json()
    print(f"JOBS: {data}")
    return data


def download_results(token: str, job_id: str):
    result = wait_for_results(token, job_id)
    if not result:
        print("Failing. Exiting.")
        return

    print(f"DOWNLOADING {job_id}")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{API_URL}/v2/jobs/{job_id}/output", headers=headers)
    response.raise_for_status()

    data = base64.b64decode(response.json().encode()).decode()
    PROJECT_OUT_PATH.write_text(json.dumps(json.loads(data), indent=4))
    print("DONE!")


def get_statuses(token: str, job_ids: list[str]):
    [get_status(token, job_id) for job_id in job_ids]


def get_status(token, job_id):
    headers = {'Authorization': f'Bearer {token}'}
    print(f"CHECKING STATUS OF: {job_id}")
    response = requests.get(f"{API_URL}/v2/jobs/{job_id}", headers=headers)
    response.raise_for_status()

    data = response.json()
    status = data["status"]
    print(f"STATUS: {status}")
    return status


def wait_for_results(token: str, job_id: str) -> bool:
    headers = {'Authorization': f'Bearer {token}'}
    status = "New"
    while status in ["New", "Started"]:
        status = get_status(token, job_id)
        if status in ["Failed", "Finished", "Abandoned"]:
            return False
        elif status == "Ready":
            return True
        else:
            print("\tWaiting 10sec")
            sleep(10)


if __name__ == "__main__":
    main()
