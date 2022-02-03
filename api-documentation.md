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
- [Retrieving Hub Data](#Retrieving-Hub-Data)

## Retrieving Hub Data 
#### `GET /Network/{hubName}`</br>
Returns all data pertaining to the Hub, its Groups, and their Projects

**Parameters:** None

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
- `endDate`

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
- `options`: <object> (More information in _Notes_ section)
  
**Returns:**
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

**Requirements:** Hub Admin
  
**Notes:** There is an option to filter the jobs that are taken into account when retrieving this data. However, this filter data must be appended to the endpoint url that is being used. This can be done by creating a string of the entire filter data, and then using the `urllib` library to parse this string into an url format.
  
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

`GET /Network/{hubName}/devices`</br>
Returns a list of data pertaining to each device within the Hub
  
**Parameters:** None
  
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
        
**Requirements:** Hub Admin
        
**Notes:** It is recommended that you parse through the returned list to retrieve the specific data you are looking for. A common piece of data you might want to parse for is `backend["name"]`.
