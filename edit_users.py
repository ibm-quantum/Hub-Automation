# (C) Copyright IBM 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import sys
import requests
import argparse
from auth import get_access_token

API_URL = "https://api-qcon.quantum-computing.ibm.com/api"

parser = argparse.ArgumentParser(description="Add or Remove groups from your Hub")
parser.add_argument('hub', type=str, help="Add or Remove groups from this Hub")
parser.add_argument('group', type=str, help="Name of parent group of project")
parser.add_argument('project', type=str, help="Name of project where user will be or is located")
parser.add_argument('action', type=str, help="Whether you are adding or removing a user. Should be set to "
                                             "either 'add' or 'remove'")
parser.add_argument('user_email', type=str, help="Email or user being added or removed")

args = parser.parse_args()

hub = args.hub
group = args.group
project = args.project
user = args.user_email
action = args.action

if action != 'remove' and action != 'add':
    sys.exit("<action> must be set ot either 'add' or 'remove'")

access_token = get_access_token()
headers = {"X-Access-Token": access_token}

# Send request to API based on what action was given
if action == "add":
    try:
        # Add user
        print(f"Adding {user} to {hub}/{group}/{project}")
        user_data = {action: [user]}  # data must be given as a list, even if only one user is being added

        # POST request to add user
        response = requests.post(url="{}/Network/{}/Groups/{}/Projects/{}/users".format(API_URL, hub, group, project),
                                 json=user_data, headers=headers)
        response.raise_for_status()  # Checks if the request returned an error
        print(f"{user} was successfully added to {hub}/{group}/{project}")
    except requests.HTTPError as http_err:
        sys.exit("Could not add user due to HTTPError: {}".format(http_err))
    except Exception as err:
        sys.exit("Could not add user due error: {}".format(err))

else:
    try:
        # Remove user
        print(f"Removing {user} from {hub}/{group}/{project}")
        user_data = {action: [user]}  # data must be given as a list, even if only one user is being removed

        # POST request to remove user
        response = requests.post(url="{}/Network/{}/Groups/{}/Projects/{}/users".format(API_URL, hub, group, project),
                                 json=user_data, headers=headers)
        response.raise_for_status()  # Checks if the request returned an error
        print(f"{user} was successfully remove from {hub}/{group}/{project}")
    except requests.HTTPError as http_err:
        sys.exit("Could not remove user due to HTTPError: {}".format(http_err))
    except Exception as err:
        sys.exit("Could not remove user due error: {}".format(err))
