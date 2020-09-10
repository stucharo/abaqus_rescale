import os
import requests

# Move this to config file when installing
RESCALE_API_KEY = os.getenv("RESCALE_API_KEY")
ABAQUS_LICENSE_SERVER = "27101@172.22.20.51"
CORE_TYPE = "emerald"
CORES_PER_SLOT = 2
ABAQUS_VERSION = "6.13-5"
ABAQUS_VERSION_CODE = "6.13.5-ibm"
RESCALE_BASE_URL = "https://platform.rescale.com/api/v2"


def run_job(job_name, input_file_path, include_file_paths=[]):
    file_ids = post_files(input_file_path, include_file_paths)
    job_id = post_job(
        job_name, os.path.basename(input_file_path), file_ids[0], file_ids[1]
    )
    submit_job(job_id)
    return job_id


def post_files(input_file_path, include_file_paths=[]):
    input_file_id = post_file(input_file_path)
    include_file_ids = [post_file(file_path) for file_path in include_file_paths]
    return (input_file_id, include_file_ids)


def post_file(filepath):
    response = requests.post(
        f"{RESCALE_BASE_URL}/files/contents/",
        headers={"Authorization": f"Token {RESCALE_API_KEY}",},
        files={"file": open(filepath, "r")},
    )
    return response.json()["id"]


def post_job(job_name, input_file_name, input_file_id, include_file_ids=[]):

    input_files = [{"id": f"{input_file_id}"}]
    for file_id in include_file_ids:
        input_files.append({"id": f"{file_id}"})

    payload = generate_post_job_json(job_name, input_file_name, input_files)

    response = requests.post(
        f"{RESCALE_BASE_URL}/jobs/",
        json=payload,
        headers={"Authorization": f"Token {RESCALE_API_KEY}"},
    )

    return response.json()["id"]


def generate_post_job_json(job_name, input_file_name, input_files):
    return {
        "name": f"{job_name}",
        "jobanalyses": [
            {
                "command": f"abaqus job={job_name} input={input_file_name} cpus=$RESCALE_CORES_PER_SLOT interactive",
                "envVars": {
                    "ADSKFLEX_LICENSE_FILE": f"{ABAQUS_LICENSE_SERVER}",
                    "LM_LICENSE_FILE": f"{ABAQUS_LICENSE_SERVER}",
                },
                "analysis": {
                    "version": f"{ABAQUS_VERSION_CODE}",
                    "code": "abaqus",
                    "name": "Abaqus",
                    "versionName": f"{ABAQUS_VERSION}",
                },
                "hardware": {
                    "coreType": f"{CORE_TYPE}",
                    "coresPerSlot": CORES_PER_SLOT,
                },
                "inputFiles": input_files,
            }
        ],
    }


def submit_job(job_id):
    requests.post(
        f"{RESCALE_BASE_URL}/jobs/{job_id}/submit/",
        headers={"Authorization": f"Token {RESCALE_API_KEY}"},
    )


def delete_file(file_id):
    response = requests.delete(
        f"{RESCALE_BASE_URL}/files/{file_id}/",
        headers={"Authorization": f"Token {RESCALE_API_KEY}"},
    )
    return response


job_id = run_job(
    "test_job", "etinde_prod_5kpa.inp", ["bathy.inc", "fix_seabed.inc", "prod_tp.inc"]
)
print(job_id)
