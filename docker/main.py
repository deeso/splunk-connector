# example usage:
# python3 mains/run_splunk_connector.py -config internal/dev-test-persist-mongo-service-config.toml

import time
import argparse
import sys
from splunk_connector.splunk_service import SplunkService
from splunk_connector.config import Config

CMD_DESC = 'start the splunk connector service.'
parser = argparse.ArgumentParser(description=CMD_DESC)
parser.add_argument('-config', type=str, default=None,
                    help='config file containing client information')

args = parser.parse_args()
if args.config is None:
    print ('config file is required')
    sys.exit(1)

Config.parse_config(args.config)
ss = SplunkService.from_config()
ss.start()
while True:
    try:
        time.sleep(60)
    except KeyboardInterrupt:
        break

ss.stop()