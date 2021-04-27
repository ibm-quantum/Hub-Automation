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
parser.add_argument('action', type=str, help="Whether you are adding or removing a group. Should be set to "
                                             "either 'add' or 'remove'")
parser.add_argument('group_name', type=str, help="Name of group being added or removed. Restricted to 16 or less chars "
                                                 "and cannot contain special chars")
parser.add_argument('-t', '--title', dest="group_title", nargs=1, type=str,
                    help="Title of group being added. Only required if <action> is set to 'add'. To have multiple "
                         "words in title, format with quotes around the title, or with underscores. "
                         "Example: 'Example Title' or Example_Title")

args = parser.parse_args()

hub = args.hub
group_name = args.group_name
action = args.action

if action != 'remove' and action != 'add':
    sys.exit("<action> must be set ot either 'add' or 'remove'")
if action == 'add':
    if not args.group_title:
        sys.exit("--title is required if <action> is set to 'add'")
    else:
        group_title = args.group_title[0]

access_token = get_access_token()
headers = {"X-Access-Token": access_token}

# Send request to API based on what action was given
if action == "add":
    try:
        if type(group_title) != str:
            sys.exit("Group Title must be a string")

        # Create Group
        group_data = {"name": group_name, "title": group_title}
        print(f"Adding {group_name} to {hub}")

        # POST request to add group
        response = requests.post(url="{}/Network/{}/Groups".format(API_URL, hub), json=group_data, headers=headers)
        response.raise_for_status()  # Checks if the request returned an error
        print(f"{group_name} was successfully added to {hub}")
    except requests.HTTPError as http_err:
        sys.exit("Could not add group due to HTTPError: {}".format(http_err))
    except Exception as err:
        sys.exit("Could not add group due error: {}".format(err))

else:
    try:
        # Delete project
        print(f"Removing {group_name} from {hub}")

        # DELETE request to remove group
        response = requests.delete(url="{}/Network/{}/Groups/{}".format(API_URL, hub, group_name), headers=headers)
        response.raise_for_status()  # Checks if the request returned an error
        print(f"{group_name} was successfully removed from {hub}")
    except requests.HTTPError as http_err:
        sys.exit("Could not remove group due to HTTPError: {}".format(http_err))
    except Exception as err:
        sys.exit("Could not remove group due error: {}".format(err))
