# Summary
There are many api endpoints that might provide useful data or perform important actions that Hub and Group admin can utilize. We hope that this documentation can be helpful in for users looking to take advantage of our api further than the provided scripts. Although there are multiple ways to use this api, the documentation below is formatted for Python, following the same structure as the scripts currently hosted in the repo.</br>

To fully understand the documentation, please refer to the below notes for details on each part of the documented entries:
- `GET`/`POST`/`DELETE`: Refers to what type of api call is made. `GET` retrieves data, `POST` posts new data entries, and `DELETE` deletes current data entries.
- **Endpoint** (Ex: `/Network/{hubName}/Groups/{groupName}`): The endpoint being called in the api call. Any part of the endpoint that is surrounded by brackets (in the example, `hubName` and `groupName` are inside of brackets) should be replaced by the user with the relevant data.
- **Parameters**: Any extra data that is needed when calling this endpoint. This data should be included in the api call by storing it in a dictionary and setting it as the `json` parameter in the `requests` call. For more information, please refer to the releveant `requests` library documentation [here](https://docs.python-requests.org/en/master/user/quickstart/#more-complicated-post-requests).
- **Returns**: The json schema of the data that is returned from the api call. You should access this data by using the `requests` library's built in json decoder. For more information, please refer to the releveant `requests` library documentation [here](https://docs.python-requests.org/en/master/user/quickstart/#json-response-content).
- **Requirements**: The required role for calling this endpoint. Typically, if the endpoint refers to Hub or Group level data, you must be a Hub admin to call it. If it refers to Project level data, you must be a Hub or Group admin. The api call will return an error if you do not have the required role.
- **Notes**: Any additional relevant information regarding the specific api call.

## Index:
- [Retrieving Hub Data](#retrieving-hub-data)
- [Managing Groups](#managing-groups)
- [Managing Projects](#managing-projects)

## Retrieving Hub Data

#### `GET /Network/{hubName}`</br>
Returns all data pertaining to the Hub, its Groups, and their Projects

**Parameters:** None</br>

**Returns:** 
  ```
  {
    "name": <str>,
    "title": <str>,
    "description": <str> (Optional),
    "creationDate": <string>,
    "deleted": <bool> (Optional),
    "ui": <object> (Optional),
    "groups": <object> (Optional),
    "devices": <object> (Optional),
    "private": <bool> (Optional),
    "licenseNotRequired": <bool> (Optional),
    "isDefault": <bool> (Optional),
    "providerNodeId": <str> (Optional),
    "analytics": <bool> (Optional),
    "class": <str> (Optional),
    "id": <str> (Optional),
    "ownerId": <str> (Optional)
  }
  ```
**Requirements:** Hub Admin</br>

**Notes:** All information about the Hub, its Groups, and each Groups' Projects are returned. It is a lot of data, so it is recommended to parse through the returned data to retrieve exactly what you need.

-----

#### `GET /Network/{hubName}/jobs/all`</br>

Returns all of the jobs run from the Hub.

**Parameters:**
- `filter`: json object (Optional, More information in _Notes_ section)

**Returns:** 
```
{
  "kind": <str>
  "backend": {
    "id": <str>,
    "name": <str>
  },
  "status": <str>,
  "creationDate": <str> (in UTC datetime format),
  "objectStorageInfo": <dict>,
  "summaryData": {
    "size": {
      "input": <int>,
      "output": <int> (Optional)
    },
    "success": <bool>,
    "summary": {
      "gates_executed": <int>,
      "qobj_config": {
        "cost": <float>,
        "rep_delay": <float>,
        "n_qubits": <int>,
        "memory_slots": <int>,
        "max_credits": <int>,
        "type": <str>,
        "shots": <int>
      },
      "num_circuits": <int>,
      "max_qubits_used": <int>,
      "partial_validation": <bool>
    }
  },
  "timePerStep": {
    "CREATING": <str> (in UTC datetime format),
    "CREATED": <str> (in UTC datetime format) (Optional),
    "VALIDATING": <str> (in UTC datetime format) (Optional),
    "VALIDATED": <str> (in UTC datetime format) (Optional),
    "QUEUED": <str> (in UTC datetime format) (Optional),
    "RUNNING": <str> (in UTC datetime format) (Optional),
    "COMPLETED": <str> (in UTC datetime format) (Optional)
  },
  "hubInfo": {
    "hub": {
      "name": <str>
    },
    "group": {
      "name": <str>
    },
    "project": {
      "name": <str>
    }
  },
  "endDate": <str> (in UTC datetime format) (Optional),
  "cost": <float>,
  "id": <str>,
  "userId": <str>,
  "infoQueue" (Optional): {
    "status": <str>,
    "position": <int>,
    "hubPriority": <float>,
    "groupPriority": <float>,
    "projectPriority": <float>,
    "estimatedStartTime": <str> (in UTC datetime format),
    "estimatedCompleteTime": <str> (in UTC datetime format)
  }
}
```

**Notes:** There is an option to filter the jobs you receive. However, this filter data must be appended to the endpoint url that is being used. This can be done by creating a string of the entire filter data, and then using the `urllib` library to parse this string into an url format. The filter is a [loop-back based filter](https://loopback.io/doc/en/lb2/Querying-data.html).

**Common stats to filter by:**</br>
- `backend.name`
- `status`
- `creationDate`
- `userId`
- `endDate`</br>

There are other stats that can also be used to filter jobs, though they are not as commonly used. You can see all stats by viewing the returned job object.

**Example**: This is an example of how to set up the filter and call the endpoint. In this example we filter for jobs run on the `backend1` after Jan 1, 2021:
```
import urllib
filters = '{"where": {"and": [{"backend.name": "backend1"}, {"creationDate": {"gt": "2021-01-01T00:00:00Z"}}]}}'
filters_url = urllib.parse.quote(filters)
# Replace <hubName> with your Hub
url = f"https://api-qcon.quantum-computing.ibm.com/api/Network/<hubName>/jobs/all?filter={param_url}"
response = requests.get(url=url, headers={"X-Access-Token": <your_access_token>})
```

-----

#### `GET /Network/{hubName}/analytics/system-usage`</br>
Returns system usage analytics pertaining to the Hub

**Parameters:**
- `options`: `<object>` (More information in _Notes_ section)</br>

**Returns:**</br>
```
{
  "data": {
    "jobs": <int>,
    "executions": <int>,
    "queueTime": <int>,
    "runTime": <int>,
    "averageRunTime": <float>,
    "averageQueueTime": <float>
  }
}
```

**Requirements:** Hub Admin</br>

**Notes:** There is an option to filter the jobs that are taken into account when retrieving this data. However, this filter data must be appended to the endpoint url that is being used. This can be done by creating a string of the entire filter data, and then using the `urllib` library to parse this string into an url format.</br>

**Options to filter by:**
- `allTime`
- `startDate`
- `endDate`
- `backend`
- `userId`
- `orderBy`
- `sort`</br>

It is required to include at least one of the following options: `allTime` or `startDate` and `endDate`. `startDate` and `endDate` take in a `datetime`, where as `allTime` should be set to `true` if being used.</br>

**Example:** This is an example of how to set up the filer and call the endpoint. In this example, we filter to only return data on jobs that were run on `backend1` between Jan 1, 2021 and Feb 1, 2021:</br>
```
import urllib
options = '{"startDate": "2021-01-01T00:00:00Z", "endDate": "2021-02-01T00:00:00Z", "backend": "backend1"}'
# If you do not require the time to be included, you can just put the date instead: "2021-01-01" and "2021-02-01
options_url = urllib.parse.quote(options)
# Replace <hubName> with your Hub
url = f"https://api-qcon.quantum-computing.ibm.com/api/Network/<hubName>/analytics/system-usage?options={options_url}"
response = requests.get(url=url, headers={"X-Access-Token": <your_access_token>})
```

-----

#### `GET /Network/{hubName}/devices`</br>
Returns a list of data pertaining to each device within the Hub

**Parameters:** None</br>

**Returns:**
```
[
  {
    "name": <str>,
    "deleted": <bool>,
    "processorType": <object>,
    "public": <bool>,
    "costParameters": <object>,
    "specificConfiguration": <object>,
    "backendName": <str>,
    "formerNames": [
      <object>
    ],
    "version": <str>,
    "address": <str>,
    "status": <str>,
    "lastConnection": <str> (in UTC time format),
    "description": <str>,
    "type": <str>,
    "docUrl": <str>,
    "gateSet": <str>,
    "basisGates": <str>,
    "oldGates": <object>,
    "oldBasisGates": <object>,
    "onlineDate": <str> (in UTC time format),
    "chipName": <str>,
    "maxQobjectSize": <int>,
    "allowObjectStorage": <bool>,
    "supportedTypes": <object>,
    "hide": <bool>,
    "statsPublic": <bool>,
    "accessType": <str>,
    "configuration": <object>,
    "inputAllowed": [
      <str>
    ],
    "capabilities": <object>,
    "geographyName": <str>,
    "category": <str>,
    "id": <str>,
    "topologyId": <str>
  }
]
```
**Requirements:** Hub Admin</br>

**Notes:** It is recommended that you parse through the returned list to retrieve the specific data you are looking for. A common piece of data you might want to parse for is `backend["name"]`.</br>

-----

### Managing Groups

`POST /Network/{hubName}/Groups`

Creates a new Group in the Hub

**Parameters:**
- `name`: `<str>` of less than or equal to 16 lowercase, non-accented characters and numbers
- `title`: `<str>`
- `priority`: `<int>`
- `description`: `<str>` (Optional)</br>

**Returns:**
```
{
  "title": <str>,
  "creationDate": <str> of UTC timestamp,
  "priorityy": <int>,
  "name": <str>,
  "projects": <object>,
  "description": <str> (Optional)
}
```
**Requirements:** Hub Admin</br>

**Notes**: `priority` represents the share that is assigned to the group. The percentage share this group will receive is equal to the `priority` given divided by the total share across all group in the hub.

-----

`POST /Network/{hubName}/Groups/{groupName}/devices`

Adds a device to the Group

**Parameters:**
- `name`: `<str>`
- `priority`: `<int>` between 1-10000</br>

**Returns:**
```
{
  <str>: {
    "priority": <int>,
    "deleted": <bool>,
    "name": <str>
  }
}
```
**Requirements:** Hub Admin</br>

**Notes:** You should input the data parameters as a dictionary in the `json` parameter for a request. This is an example:</br>
```
data = {"name": "device_name", "priority": 1}
response = requests.post(url=url, json=data)
```

-----

`GET /Network/{hubName}/Groups/{groupName}/jobs/all`

Returns data about jobs that were sent from any Project within this Group

**Parameters:**
- `filter`: json object (Optional, More information in _Notes_ section)</br>

**Returns:** 
```
{
  "kind": <str>
  "backend": {
    "id": <str>,
    "name": <str>
  },
  "status": <str>,
  "creationDate": <str> (in UTC datetime format),
  "objectStorageInfo": <dict>,
  "summaryData": {
    "size": {
      "input": <int>,
      "output": <int> (Optional)
    },
    "success": <bool>,
    "summary": {
      "gates_executed": <int>,
      "qobj_config": {
        "cost": <float>,
        "rep_delay": <float>,
        "n_qubits": <int>,
        "memory_slots": <int>,
        "max_credits": <int>,
        "type": <str>,
        "shots": <int>
      },
      "num_circuits": <int>,
      "max_qubits_used": <int>,
      "partial_validation": <bool>
    }
  },
  "timePerStep": {
    "CREATING": <str> (in UTC datetime format),
    "CREATED": <str> (in UTC datetime format) (Optional),
    "VALIDATING": <str> (in UTC datetime format) (Optional),
    "VALIDATED": <str> (in UTC datetime format) (Optional),
    "QUEUED": <str> (in UTC datetime format) (Optional),
    "RUNNING": <str> (in UTC datetime format) (Optional),
    "COMPLETED": <str> (in UTC datetime format) (Optional)
  },
  "hubInfo": {
    "hub": {
      "name": <str>
    },
    "group": {
      "name": <str>
    },
    "project": {
      "name": <str>
    }
  },
  "endDate": <str> (in UTC datetime format) (Optional),
  "cost": <float>,
  "id": <str>,
  "userId": <str>,
  "infoQueue" (Optional): {
    "status": <str>,
    "position": <int>,
    "hubPriority": <float>,
    "groupPriority": <float>,
    "projectPriority": <float>,
    "estimatedStartTime": <str> (in UTC datetime format),
    "estimatedCompleteTime": <str> (in UTC datetime format)
  }
}
```
**Notes:** There is an option to filter the jobs you receive. However, this filter data must be appended to the endpoint url that is being used. This can be done by creating a string of the entire filter data, and then using the `urllib` library to parse this string into an url format. The filter is a [loop-back based filter](https://loopback.io/doc/en/lb2/Querying-data.html).</br>

**Common stats to filter by:**</br>
- `backend.name`
- `status`
- `creationDate`
- `userId`
- `endDate`</br>

There are other stats that can also be used to filter jobs, though they are not as commonly used. You can see all stats by viewing the returned job object.</br>

-----

`POST /Network/{hubName}/Groups/{groupName}/users`

Add or Remove a user as an admin to the Group

**Parameters:** 
- `add`: List of objects containing user emails being added as admin. If no users are being added, you can ignore putting this parameter completely. For more information on the format of this parameter, refer to _Notes_ section.
- `remove`: List of user emails being removed from admin role. If no users are being removed, you can ignore putting this parameter completely. For more information on the format of this parameter, refer to _Notes_ section.

**Returns:**
```
{
  "added": {
    "name": <str>,
    "projects": <object>,
    "users": {
      <str>: {
        "role": <str>,
        "deleted": <bool>,
        "email": <str>,
        "name": <str>,
        "dateJoined": <str> (in UTC datetime format)
      },
    },
    "deleted": <bool>
  }
}
```
**Requirements:** Hub Admin or Group Admin</br>

**Notes:** There is a specific format that the parameters must follow, or else you will receive an error. Here is an example for using each parameter:
```
# Data format for adding admin
data = {"add": [{"email": "email@example.com", "role": "admin"}, ...]} 

# Data format for removing admin
data = {"remove": ["email@example.com", ...]}

# You must wrap the user objects in a list, even if you are only adding 1 admin!

# You can add and remove admin within the same call
data = {"add": [{"email": "email@example.com", "role": "admin"}, ...], "remomve": ["email@example.com", ...]} 
```

-----

`GET /Network/{hubName}/Groups/{groupName}/devices/{deviceName}/configurationDetails`

Returns the configuration data set for the specified device in the Group

**Parameters**: None</br>

**Returns:**
```
{
  "capabilities": {
    "openPulse": <bool>,
    "maxExperiments": <int> (Optional),
    "maxShots": <int> (Optional),
    "pulseQubits": <int> (Optional),
    "pulseChannels": <int> (Optional)
  },
  "limit": <int>
}
```
**Requirements:** Hub Admin</br>

**Notes:** You will not always see all of this data returned. The only data that is included in the returned json object are attributes that were manually set when adding the device. For attributes where the default setting was used, their data will not be returned. You should also disregard the `limit` attribute.

-----

`GET /Network/{hubName}/devices/{deviceName}/configurationDetails`

Returns the configuration data set for the specified device in the Hub

**Parameters**: None</br>

**Returns:**
```
{
  "capabilities": {
    "openPulse": <bool>,
    "maxExperiments": <int> (Optional),
    "maxShots": <int> (Optional),
    "pulseQubits": <int> (Optional),
    "pulseChannels": <int> (Optional)
  },
  "limit": <int>
}
```
**Requirements:** Hub Admin</br>

**Notes:** You will not always see all of this data returned. The only data that is included in the returned json object are attributes that were manually set when adding the device. For attributes where the default setting was used, their data will not be returned. You should also disregard the `limit` attribute.

-----

`DELETE /Network/{hubName}/Groups/{groupName}/devices/{deviceName}`

Remove the specified device from the given Group

**Parameters:** None</br>

**Returns**:
```
{
  "deleted": <bool>
}
```

**Requirements**: Hub Admin

-----

### Managing Projects

`POST /Network/{hubName}/Groups/{groupName}/Projects`

Create a new Project in the given Hub and Group

**Parameters:**
- `name`: `<str>` of less than or equal to 16 lowercase, non-accented characters and numbers
- `title`: `<str>`
- `priority`: `<int>`
- `description`: `<str>` (Optional)</br>

**Returns**: 
```
{
    "title": <str>,
    "creationDate": <str> of UTC timestamp,
    "priorityy": <int>,
    "description": <str> (Optional),
    "name": <str>
}
```
**Requirements**: Hub Admin or Group Admin</br>

**Notes**: `priority` represents the share that is assigned to the project. The percentage share this project will receive is equal to the `priority` given divided by the total share across all projects in the group.

-----

`DELETE /Network/{hubName}/Groups/{groupName}/Projects/{projectName}`

Deletes a Project from the Group

**Parameters:** None</br>

**Returns**:
```
{
  "deleted": <object>
}
```
**Requirements**: Hub Admin or Group Admin</br>

-----

`GET /Network/{hubName}/Groups/{groupName}/Projects/{nameProject}/devices`

Returns a list of data about accessible devices within the Project

**Parameters:** None</br>

**Returns**:<br>
```
[
  {
    "acquisition_latency": <list>,
    "allow_q_object": <bool>,
    "backend_name": <str>,
    "backend_version": <str>,
    "basis_gates": <list>
    "channels": {
      "acquire0": {
        "operates": {
          "qubits": <list>
        },
        "purpose": <str>,
        "type": <str>
      },
      "d0": {
        "operates": {
          "qubits": <list>
        },
        "purpose": <str>,
        "type": <str>
      },
      "m0": {
        "operates": {
          "qubits": <list>
        },
        "purpose": <str>,
        "type": <str>
      }
    },
    "clops": <int>,
    "conditional": <bool>,
    "conditional_latency": <list>,
    "coupling_map": <list>,
    "credits_required": <bool>,
    "description": <str>,
    "discriminators": <list>,
    "dt": <float>,
    "dtm": <float>,
    "dynamic_reprate_enabled": <bool>,
    "gates": [
      {
        "coupling_map": <list>,
        "name": <str>,
        "parameters": <list>,
        "qasm_def": <str>
      },
    ],
    "hamiltonian": {
      "description": "<str>",
      "h_latex": <str>,
      "h_str": <list>,
      "osc": <dict>,
      "qub": <dict>,
      "vars": <dict>
    },
    "local": <bool>,
    "max_experiments": <int>,
    "max_shots": <int>,
    "meas_kernels": <list>,
    "meas_levels": <list>,
    "meas_lo_range": <list>,
    "meas_map": <list>,
    "measure_esp_enabled": <bool>,
    "memory": <bool>,
    "multi_meas_enabled": <bool>,
    "n_qubits": <int>,
    "n_registers": <int>,
    "n_uchannels": <int>,
    "online_date": <str>,
    "open_pulse": <bool>,
    "parametric_pulses": <list>,
    "processor_type": <dict>
    "quantum_volume": <int>,
    "qubit_channel_mapping": <list>,
    "qubit_lo_range": <list>,
    "rep_times": <list>,
    "sample_name": <str>,
    "simulator": <bool>,
    "supported_features": <list>,
    "supported_instructions": <list>,
    "timing_constraints": <dict>,
    "u_channel_lo": <list>,
    "uchannels_enabled": <bool>,
    "url": <str>,
    "input_allowed": <list>,
    "allow_object_storage": <bool>,
    "pulse_num_channels": <int>,
    "pulse_num_qubits": <int>
  }
]
```

**Requirements**: Hub Admin

**Notes:** Each entry in the returned list will contain a lot of data. It is recommended that you parse through the returned jsons to retrieve the specific data you are looking for. The most common piece of data you will parse for is `backend["name"]`.</br>

----

`POST /Network/{hubName}/Groups/{groupName}/Projects/{projectName}/devices`

Adds a device to the Project

**Parameters:**
- `name`: `<str>`
- `priority`: `<int>` between 1-10000</br>

**Returns:** None</br>

**Requirements:** Hub Admin or Group Admin</br>

**Notes:** You should input the data parameters as a dictionary in the `json` parameter for a request. This is an example:</br>
```
data = {"name": <device_name>, "priority": 1}
response = requests.post(url=url, json=data)
```

-----

`GET /Network/{hubName}/Groups/{groupName}/Projects/{projectName}/jobs/all`

Returns data about jobs that were sent from Project

**Parameters:** None</br>

**Returns**: List containing json objects with the following schema:</br>
```
{
  "kind": <str>,
  "backend": {
      "id": <str>,
      "name": <str>
  },
  "status": <str>,
  "creationDate": <str>,
  "objectStorageInfo": <dict>,
  "summaryData": {
      "size": {
          "input": <int>,
          "output": <int>
      },
      "success": <bool>,
      "summary": {
          "max_qubits_used": <int>,
          "qobj_config": {
              "memory_slots": <int>,
              "rep_delay": <int>,
              "n_qubits": <int>,
              "type": <str>,
              "shots": <int>,
              "cost": <float>
          },
          "partial_validation": <bool>,
          "gates_executed": <int>,
          "num_circuits": <int>
      },
      "resultTime": <float>
  },
  "timePerStep": {
      "CREATING": <str>,
      "CREATED": <str>,
      "VALIDATING": <str>,
      "VALIDATED": <str>,
      "QUEUED": <str>,
      "RUNNING": <str>,
      "COMPLETED": <str>
  },
  "hubInfo": {
      "hub": {
          "name": <str>
      },
      "group": {
          "name": <str>
      },
      "project": {
          "name": <str>
      }
  },
  "endDate": <str>,
  "cost": <float>,
  "runMode": <str>,
  "id": <str>,
  "userId": <str>
}
```
**Requirements**: Hub Admin or Group Admin</br>

**Notes**: All of the values returned for `creationDate`, all steps in `timePerStep`, `estimatedStartTime` and `estimatedCompleteTime` in `infoQueue`, and `endDate` will always be strings in the format of a date in the UTC timezone. For example: `2022-06-29T08:02:00.550Z` would represent June 29, 2022 at 8:02am UTC

-----

`POST /Network/{hubName}/Groups/{groupName}/Projects/{projectName}/users`

Add or Remove a user from the Project

**Parameters:** Only one of `add` or `remove` is required. If you only want to add or remove users, you do not need to include the other parameter.
```
{
    "add":
        [<email>, ...],
    "remove":
        [<email>, ...],
}
```

**Returns**:
```
{
  "added": {
    "name": <str>,
    "users": {
      <str>: {
        "deleted": <bool>,
        "email": <str>,
        "name": <str>,
        "dateJoined": "2022-02-01T21:28:48.965Z"
      }
    },
    "deleted": <bool>
  }
}
```

**Requirements**: Hub Admin

-----

`DELETE /Network/{hubName}/Groups/{groupName}/Projects/{projectName}/devices/{deviceName}`

Deletes the device from the Project

**Parameters:** None</br>

**Returns**:<br>
```
{
    "deleted": <bool>
}
```

**Requirements**: Hub Admin or Group Admin
