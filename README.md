# splunk-connector

The splunk-connector module is a library that aims to simply named and unamed splunk queries.  Currently,
the project simplifies the configuration of a Splunk client, searching by tags, and searching with a raw query.

There are a number of ways this project could extended, so if you have ideas, feel free to open an issue.


## Setup and installation

Currently, this code runs on Ubuntu Linux 18.04 and requires Python 3.6+ and an account on a Splunk instance.

```bash
mkdir sc-work
cd sc-work

# install dependencies
sudo apt-get install -y python3-venv unzip git python3-dev

# disable SSL verification, generally insecure
git config --global http.sslVerify false

# setting up runtime environment
python3 -m venv splunk_connector

cd ../
git clone https://github.com/deeso/splunk-connector
source bin/activate
pip3 install ipython
cd splunk-connector
python3 setup.py install
```

## Configuration

There is a basic configuration in the source directory and another more complete example 

The configuration file contains to types of stanzas: 
1. `Service` in `connector.py`
1. `NamedSplunkQuery` in `query.py`

The simplest way to parse a config file is to use `Services` in `connector.py`.  This class will:
1. *Parse* the file
2. *Create* the dictionaries required to build the objects
3. *Build* the `Service` and `NamedSplunkQuery` objects
4. *Associate* `NamedSplunkQuery`s with their respective `Service`

### `NamedSplunkQuery` configuration stanzas
```toml
[splunk-query.required_name]   # this required_value will be used if a Name is not provided
name = 'optional-name'         # optional name, if not provided the required_name will be used
sensitive = false              # query results in sensitive data 
tags = ['tag1', 'tag2']        # tags this query is associated with
query = """                    
search earliest={earliest} 
{user_query}
  |uniq
"""                            # multiline query string, note '\'- needs to be escaped, see TOML docs.
parameter_names = ['earliest', 'user_query']  # parameters from query that are used to build variable query elements

[splunk-query.required_name2]   # this required_value will be used if a Name is not provided
sensitive = false              # query results in sensitive data 
tags = ['tag4', 'tag2']        # tags this query is associated with
query = """                    
search vpn |uniq               
"""                            # simple query with no parameters
                               # parameters from query that are used to build variable query elements
```

### `Service` configuration stanzas
```toml
[splunk-service.required_value]      # this required_value will be used if a Name is not provided
name = 'optional-name'
host = 'hostname.localhost'          # (default: 127.0.0.1) hostname of the splunk service
port = 8089                          # (default: 8000) port used by the splunk server
username = 'USERNAME'                # (default: None) username
password = 'PASSWORD'                # (default: None) password

[splunk-service.required_value2]
host = 'hostname2.localhost'
port = 8089
username = 'USERNAME_0'
password = 'PASSWORD_1'

``` 

## Using the library

Here are some examples.

- Searching for VPN users using 
```python
import json
from datetime import datetime, timedelta
from splunk_connector.connector import Services
from getpass import getpass
from splunk_connector.consts import *


config = 'sample-splunk-connector.toml'
svcs = Services(config_file=config)

service = svcs.services['sname']

# TODO enter your password if not set in the config
set_password_username = False
if set_password_username:
    service.username = 'USERNAME'
    service.password = getpass('enter password:  ')

# we are looking for the current user's VPN logs for the last 10 days
dateformat='%m/%d/%Y:%H:%M:%S'
now = datetime.utcnow() 
dt = now - timedelta(days=10)

# set up the parameterized values for the query
USERS = ['bob', 'alice', 'malice']

user_list = [
  {'username': 'username', 'mail': 'username@example.com'},
]
# helper using lambdas to build the required parameter dictionaries

parameter_dict = service.build_parameter_dict({"user_query": user_list,
                                                      "earliest": dt.strftime(dateformat),
                                                      "latest":now.strftime(dateformat)
                                                      })


job_keywords = {
    "latest_time": "now",
    "output_mode": "json",
    "search_mode": "normal",
    "blocking": True,
}

splunk_results_dict = service.perform_stored_query("vpn", parameter_dict=parameter_dict,
                                                   job_keywords=job_keywords)

svc = splunk_results_dict[SPLUNK_QUERY_SVC]
rsp = splunk_results_dict[SPLUNK_QUERY_RSP]


print ("Performed the following query: %s"%splunk_results_dict[SPLUNK_QUERY_QUERY])

# read the responses from the services
data = results['data']
print(json.dumps({k:v for k,v in results.items() if k not in [SPLUNK_QUERY_RSP, SPLUNK_QUERY_SVC, SPLUNK_QUERY_DATA]}, 
                 indent=4, sort_keys=True))

# convert the data response to JSON
json_data = []
for line in data.splitlines():
   json_data.append(json.loads(line))
   
print(json.dumps(json_data, indent=4, sort_keys=True))

```
