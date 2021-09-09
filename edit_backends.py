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
import json
from auth import get_access_token

API_URL = "https://api-qcon.quantum-computing.ibm.com/api"

parser = argparse.ArgumentParser(description="Add or Remove a backend from a Project in the Hub")
parser.add_argument('hub', type=str, help="The Hub to manage backends on")
parser.add_argument('action', type=str, choices=['add', 'remove'], help="Whether or not to add or remove the backend from a project")
parser.add_argument('group', type=str, help="Name of the group to manage backends for")
parser.add_argument('backend', type=str, help="Name of the backend to be added or removed")
parser.add_argument('-project', type=str, help="Name of the project to manage backends for")
parser.add_argument('-priority', type=int, help="Priority of the backend. Must be an integer between 1 and 10,000")
args = parser.parse_args()

hub = args.hub
action = args.action
group = args.group
project = args.project
backend = args.backend
priority = args.priority

access_token = get_access_token()
headers = {'X-Access-Token': access_token}

# Need to check for the presence of a priority value if adding a backend
if action == 'add':
	if priority is None or priority not in range(1, 10001):
		sys.exit('You must provide a priority between 1 and 10,000. Use the -h parameter for more info')

# Make the API request and handle errors
try:
	if action == 'add':
		if project is not None:
			url = f'{API_URL}/Network/{hub}/Groups/{group}/Projects/{project}/devices'
		else:
			url = f'{API_URL}/Network/{hub}/Groups/{group}/devices'

		response = requests.post(url, headers=headers, json={'name': backend, 'priority': priority})
	else:
		if project is not None:
			url = f'{API_URL}/Network/{hub}/Groups/{group}/Projects/{project}/devices/{backend}'
		else:
			url = f'{API_URL}/Network/{hub}/Groups/{group}/devices/{backend}'

		response = requests.delete(url, headers=headers)

	s = f'{hub} (group: {group} and project: {project})'
	response.raise_for_status()
except requests.HTTPError as http_err:
	sys.exit(f"Could not edit backends in {s} due to HTTPError: {http_err}")
except Exception as err:
	sys.exit(f"Could not edit backends in {s} due to: {err}")

data = response.json()
print(json.dumps(data, indent=4))
