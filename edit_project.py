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
parser.add_argument('group', type=str, help="Name of parent group of project being added or removed")
parser.add_argument('action', type=str, help="Whether you are adding or removing a group. Should be set to "
                                             "either 'add' or 'remove'")
parser.add_argument('project_name', type=str, help="Name of project being added or removed. Restricted to 16 or less "
                                                  "chars and cannot contain special chars")
parser.add_argument('-t', '--title', dest="project_title", nargs=1, type=str,
                    help="Title of project being added. Only required if <action> is set to 'add'. To have multiple "
                         "words in title, format with quotes around the title, or with underscores. "
                         "Example: 'Example Title' or Example_Title")
parser.add_argument('-s', '--share', dest="share", nargs=1, type=int,
                    help="Share value set for this project. Only required if <action> is set to 'add'")

args = parser.parse_args()

hub = args.hub
group = args.group
project_name = args.project_name
priority = args.share
action = args.action

if action != 'remove' and action != 'add':
    sys.exit("<action> must be set ot either 'add' or 'remove'")
if action == 'add':
    if not args.project_title:
        sys.exit("--title is required if <action> is set to 'add'")
    else:
        project_title = args.project_title[0]

access_token = get_access_token()
headers = {"X-Access-Token": access_token}

# Send request to API based on what action was given
if action == "add":
    try:
        if type(project_title) != str:
            sys.exit("Project Title must be a string")

        # Create project
        project_data = {"name": project_name, "title": project_title, "priority": priority}
        print(f"Adding {project_name} to {hub}/{group}")

        # POST request to add project
        response = requests.post(url="{}/Network/{}/Groups/{}/Projects".format(API_URL, hub, group),
                                 json=project_data, headers=headers)
        response.raise_for_status()  # Checks if the request returned an error
        print(f"{project_name} was successfully added to {hub}/{group}")
    except requests.HTTPError as http_err:
        print("Could not add project due to HTTPError: {}".format(http_err))
    except Exception as err:
        print("Could not add project due error: {}".format(err))
elif action == "remove":
    try:
        # Delete project
        print(f"Removing {project_name} from {hub}/{group}")

        # DELETE request to remove project
        response = requests.delete(url="{}/Network/{}/Groups/{}/Projects/{}".format(API_URL, hub, group, project_name),
                                   headers=headers)
        response.raise_for_status()  # Checks if the request returned an error
        print(f"{project_name} was successfully removed from {hub}/{group}")
    except requests.HTTPError as http_err:
        print("Could not remove project due to HTTPError: {}".format(http_err))
    except Exception as err:
        print("Could not remove project due error: {}".format(err))
else:
    sys.exit("Please input either 'add' or 'remove' for the <action> parameter")
