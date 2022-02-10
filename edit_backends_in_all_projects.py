# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import requests
import argparse
import sys
import time
from auth import get_access_token

API_URL = "https://api-qcon.quantum-computing.ibm.com/api"

parser = argparse.ArgumentParser(description="Add or Remove a backend from all Projects in the given Hub/Group")
parser.add_argument('hub', type=str, help="The Hub that contains the given Group")
parser.add_argument('action', type=str, choices=['add', 'remove'], help="Whether or not to add or remove the backend from all projects")
parser.add_argument('group', type=str, help="Name of the group to add/remove the given backend from all Projects")
parser.add_argument('backend', type=str, help="Name of the backend to be added or removed")
parser.add_argument('-priority', type=int, help="Priority of the backend (if adding). Must be an integer between 1 and 10000")
args = parser.parse_args()

hub = args.hub
action = args.action
group = args.group
backend = args.backend
priority = args.priority

access_token = get_access_token()
headers = {'X-Access-Token': access_token}

# Need to check for the presence of a priority value if adding a backend
if action == 'add':
    if priority is None or priority not in range(1, 10001):
        sys.exit('You must provide a priority between 1 and 10000. Use the -h flag for more info')
else:
    if priority is not None:
        print("You do not need to use the -priority arg when removing systems")


# Get names of Projects in Group
projects_list = []
try:
    url = f'{API_URL}/Network/{hub}'
    response = requests.get(url=url, headers=headers)

    response.raise_for_status()
    hub_data = response.json()

    if "groups" in hub_data and "projects" in hub_data["groups"][group]:
        for project in hub_data["groups"][group]["projects"].values():
            projects_list.append(project["name"])
except requests.HTTPError as http_err:
    sys.exit(f"Could not get hub data due to HTTPError: {http_err}")
except Exception as err:
    sys.exit(f"Could not get hub data due to: {err}")


# Call API to add or remove backend from all Projects found in Group
if action == 'add':
    for project in projects_list:
        try:
            time.sleep(2)
            url = f'{API_URL}/Network/{hub}/Groups/{group}/Projects/{project}/devices'
            response = requests.post(url, headers=headers, json={'name': backend, 'priority': priority})
            response.raise_for_status()
            print(f"{backend} was added to {project}")
        except requests.HTTPError as http_err:
            sys.exit(f"Could not add {backend} to {project} due to HTTPError: {http_err}")
        except Exception as err:
            sys.exit(f"Could not add {backend} to {project} due  due to: {err}")
    print(f"{backend} has been added to all projects in {group}")

else:
    for project in projects_list:
        try:
            time.sleep(2)
            url = f'{API_URL}/Network/{hub}/Groups/{group}/Projects/{project}/devices'
            response = requests.get(url, headers=headers)
            data = response.json()
            project_devices = [x['backend_name'] for x in data]
            response.raise_for_status()
            if backend not in project_devices:
                print(f"{project} does not have access to {backend}. Skipping...")
            else:
                url = f'{API_URL}/Network/{hub}/Groups/{group}/Projects/{project}/devices/{backend}'
                response = requests.delete(url, headers=headers)
                response.raise_for_status()
                print(f"{backend} was removed from {project}")
        except requests.HTTPError as http_err:
            sys.exit(f"Could not remove {backend} to {project} due  due to HTTPError: {http_err}")
        except Exception as err:
            sys.exit(f"Could not remove {backend} to {project} due  due to: {err}")
    print(f"{backend} has been deleted from all projects in {group}")