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

parser = argparse.ArgumentParser(description="Retrieve backend system information from your entire Hub or a specific Project")
parser.add_argument('hub', type=str, help="The Hub to retreive backend information from")
parser.add_argument('-group', type=str, help="Name of the group to retrieve backends from")
parser.add_argument('-project', type=str, help="Name of the project to retrieve backends from")
parser.add_argument('--full_data', action="store_true", help="Print out the full JSON response for all backend data")

args = parser.parse_args()

hub = args.hub
group = args.group
project = args.project
full_data = args.full_data

access_token = get_access_token()
headers = {'X-Access-Token': access_token}

# Determine which URL to use- either it is a request for the entire Hub's devices or a specific project's devices.
# The group and project arguments are mutually inclusive so validate that.
if group is None and project is None:
	url = f'{API_URL}/Network/{hub}/devices'
	s = hub
elif group is not None and project is not None:
	url = f'{API_URL}/Network/{hub}/Groups/{group}/Projects/{project}/devices'
	s = f'{hub} (group: {group} and project: {project})'
else:
	sys.exit("You must provide both -group and -project arguments, use the -h parameter for more information")

# Make the API request and handle errors
try:
    response = requests.get(url=url, headers=headers)
    response.raise_for_status()  # Checks if the request returned an error
except requests.HTTPError as http_err:
    sys.exit(f"Could not retrieve backend information in {s} due to HTTPError: {http_err}")
except Exception as err:
    sys.exit(f"Could not retrieve backend information in {s} due to: {err}")

data = response.json()
if full_data:
	print(json.dumps(data, indent=4, sort_keys=True))

# Print a list of backend names only
backends = []
for obj in data:
	# Depending on which API endpoint was hit- the location of the backend_name string differs
	if 'specificConfiguration' in obj:
		backends.append(obj['specificConfiguration']['backend_name'])
	else:
		backends.append(obj['backend_name'])

print(backends)
