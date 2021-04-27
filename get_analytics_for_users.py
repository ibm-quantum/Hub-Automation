# (C) Copyright IBM 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import requests
import csv
import time
import urllib
import sys
import warnings
import datetime
import argparse
from auth import get_access_token

API_URL = "https://api-qcon.quantum-computing.ibm.com/api"

access_token = get_access_token()
headers = {'X-Access-Token': access_token}

parser = argparse.ArgumentParser(description="Retrieve analytics for given users on given backends over a given date "
                                             "range. Users, backends, and date ranges are pulled from "
                                             "analytics_data.csv, which must be located in the same directory")
parser.add_argument('hub', type=str, help="The Hub analytics are retrieved for")

args = parser.parse_args()

hub = args.hub

# ---------------------------------------------------------------
# Helper functions


def is_date_range_valid(start_date, end_date):
    '''Compares the start_date and end_date datettime objects to confirm that end_date is greater than start_date

        Returns True is end_date is a datettime that comes after start_date. Else, returns False'''
    start_sections = list(map(lambda x: int(x), start_date.split('-')))
    end_sections = list(map(lambda x: int(x), end_date.split('-')))

    start_date = datetime.date(start_sections[2], start_sections[0], start_sections[1])
    end_date = datetime.date(end_sections[2], end_sections[0], end_sections[1])

    if start_date > end_date:
        return False

    return True


def extract_user_ids(user_dict, data):
    '''Extracts the user_id from <data> for all users included in <user_dict> and stores them
        as the <id> value for the user's entry in <user_dict>'''
    for user in data:
        user_data = data[user]
        email = user_data['email']
        if email in user_dict.keys():
            user_dict[email]['id'] = user

    return user_dict


# ---------------------------------------------------------------
# Open the analytics_data.csv file and extract the data. Data is stored in the 'users' dictionary.

'''
Format for the <users> dictionary:
    {
    email: {
        id: <str>,
        backends: <list>, 
        start: <str>, 
        end: <str>
        }
    }
'''
users = {}

with open("analytics_data.csv", "r") as file:
    reader = csv.reader(file)
    for idx, row in enumerate(reader):
        if idx != 0:
            start_date = row[0]
            end_date = row[1]
            if end_date != '' and start_date != '' and not is_date_range_valid(start_date, end_date):
                sys.exit(f"Error: end_date ({end_date}) cannot come before start_date ({start_date})")
            user = row[2]
            backends = row[3].replace(' ', '').split(',')
            if user in users:
                warnings.warn(f"Warning: duplicate entry of {user} found. Discarding the duplicate.")
            else:
                users[user] = {'id': '', 'backends': backends, 'start': start_date, 'end': end_date}

    file.close()

# ---------------------------------------------------------------
# Retrieve user_ids for all users extracted from the data file.


# Send request to API to retrieve all users in hub.
url = f'{API_URL}/Network/{hub}/users'

try:
    response = requests.get(url=url, headers=headers)
    response.raise_for_status()  # Checks if the request returned an error
except requests.HTTPError as http_err:
    sys.exit(f"Could not retrieve users in {hub} due to HTTPError: {http_err}")
except Exception as err:
    sys.exit(f"Could not retrieve users in {hub} due to HTTPError: {err}")

data = response.json()

'''
Format for the returned data:

data: {
    users: {
        user_id: {
            role: <str>,
            deleted: <bool>,
            email: <str>,
            name: <str>,
            dateJoined: <str>
        }
    },
    groups: {
        group_name: {
            name: <str>,
            projects: {
                project_name: {
                    name: <str>,
                    users: {
                        user_id: {
                            deleted: <bool>,
                            email: <str>,
                            name: <str>,
                            dateJoined: <str>
                        }
                    },
                    deleted: <bool>            
                }
            }
            users: {
                user_id: {
                    role: <str>,
                    deleted: <bool>,
                    email: <str>,
                    name: <str>,
                    dateJoined: <str>
                }
            }
        } 
    },
    hubId: <str>,
    id: <str>
}
'''

# Check if Hub admin are in the query data and extract and store their userIds
extract_user_ids(users, data["users"])

# Check if Group admin are in the query data and extract and store their userIds
for group in data["groups"].values():
    extract_user_ids(users, group["users"])
    # Check if Project collaborators are in the query data and extract and store their userIds
    if "projects" in group:
        for project in group["projects"].values():
            extract_user_ids(users, project["users"])

# ---------------------------------------------------------------
# Get analytics for each user and store in user_stats dict

'''
Format for user_stats:
    {
    email: {
        backend: {
            'averageQueueTime': <int>,
            'averageRunTime': <int>,
            'executions': <int>,
            'jobs': <int>,
            'queueTime': <int>,
            'runTime': <int>
            }
        }
    }
'''
user_stats = {}

# Parse through users dict and use data to send request to API to retrieve analytics for each user.
for user in users:
    start_date = users[user]["start"]
    end_date = users[user]["end"]
    backends = users[user]["backends"]
    id = users[user]["id"]

    # Send individual request to API for analytics for each backend included in user data
    for backend in backends:
        time.sleep(5)  # Prevent DDOS kickout

        # Create options string with parameters specifying backend, user, and date range to return analytics for
        if start_date == '' or end_date == '':
            options = '{{"allTime": true,"backend":"{}", "userId":"{}"}}'.format(backend, id)
        else:
            options = '{{"startDate":"{}","endDate":"{}","backend":"{}", "userId":"{}"}}'.format(start_date, end_date,
                                                                                                 backend, id)

        # Convert options string into url friendly format
        options_url = urllib.parse.quote(options)

        # Send request to API to retrieve analytics
        url = f'{API_URL}/Network/{hub}/analytics/system-usage?options={options_url}'

        try:
            print(f"Retrieving {user}'s usage stats on {backend}...")
            response = requests.get(url=url, headers=headers)
            response.raise_for_status()  # Checks if the request returned an error
        except requests.HTTPError as http_err:
            sys.exit(f"Could not retrieve analytics for {user} due to HTTPError: {http_err}")
        except Exception as err:
            sys.exit(f"Could not retrieve analytics for {user} due error: {err}")

        '''
        Format for returned data:
            data: {
                jobs: <int>,
                executions: <int>,
                queueTime: <int>,
                runTime: <int>,
                averageRunTime: <int>,
                averageQueueTime: <int>
            }
        '''
        data = response.json()

        # Store returned data in user_stats dict
        current_data = user_stats.get(user, {})
        current_data[backend] = data["data"]
        user_stats[user] = current_data


# ---------------------------------------------------------------
# Create new .csv file and write results to file


with open("analytics_results.csv", "w") as file:
    writer = csv.writer(file)

    # Write header cells for all returned data
    writer.writerow(["User", "Backend", "Jobs", "Executions", "Queue Time (ms)", "Run Time (ms)",
                     "Average Run Time (ms)", "Average Queue Time (ms)", "Date Range"])

    print(f"Starting to write analytics to {file.name}")

    # Parse through users in user_stats dict
    for user, stats_dict in user_stats.items():
        # Parse through backends for user
        for backend, usage_stats in stats_dict.items():
            print(f"Writing analytics for {user} on {backend}")

            # Write values for each data field to the user's row
            next_row = [user, backend]
            for stat in usage_stats.values():
                next_row.append(stat)

            # Write date range to row or all time
            if users[user]["start"] == '' or users[user]["end"] == '':
                next_row.append("All Time")
            else:
                next_row.append(f"{users[user]['start']} - {users[user]['end']}")
            writer.writerow(next_row)

    file.close()

print("Finished retrieving analytics. You can view the results in analytics_results.csv")
