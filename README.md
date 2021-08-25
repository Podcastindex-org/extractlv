# extractlv
Tools for extracting TLV's from a lightning node and doing cool things with them.

INSTALLATION INSTRUCTIONS

Tested on Python 3.7.3
Refer: https://github.com/lightningnetwork/lnd/blob/master/docs/grpc/python.md

Ubuntu: (Steps tested on 19.04, should be similar on more recent releases)
- Ensure python3 --version reports 3.7.3 or above
- If you're using an OLD distro like 19.04, you'll probably need to grab the archived repos: 
- - sudo sed -i -re 's/([a-z]{2}\.)?archive.ubuntu.com|security.ubuntu.com/old-releases.ubuntu.com/g' /etc/apt/sources.list
- - sudo apt-get update && sudo apt-get dist-upgrade
- Install pip3 if not already installed, install it from the default repo, but then upgrade pip and wheel to the latest versions immediately afterward:
- - sudo apt install python3-pip
- - sudo -H pip3 install --upgrade pip
- - pip3 install --upgrade wheel
- - pip3 install testresources setuptools
- Install the libraries needed for PIP to install the gRPC tools we need to use: 
- - sudo apt-get install libnss3 libnss3-dev libcurl4-gnutls-dev librtmp-dev
- Finally, you can install the tools themselves:
- - pip3 install grpcio grpcio-tools googleapis-common-protos git curl pycurl

On a Raspiblitz things are easier since most of the above tools have already been installed:
- - pip3 install grpcio grpcio-tools googleapis-common-protos
- Note: Upgrade to latest grpcio just in case:
- - pip3 install --upgrade grpcio
- From your home directory on the blitz, clone two Git Repos, and download the proto file you need:
- - git clone https://github.com/daveajones/extractlv
- - cd extractlv
- - git clone https://github.com/googleapis/googleapis.git
- - curl -o lightning.proto -s https://raw.githubusercontent.com/lightningnetwork/lnd/master/lnrpc/lightning.proto
- Finally, compile the required tool files:
- - python3 -m grpc_tools.protoc --proto_path=googleapis:. --python_out=. --grpc_python_out=. lightning.proto

USAGE AND CONFIGURATION

This simple script can be used in conjunction with the PushOver notification service to send a message once a Boost-A-Gram is received. Go to Pushover.Net and create an application for the Notifier, then add your PUSHOVER_USER_TOKEN and PUSHOVER_API_TOKEN to the Definitions section of the script. You can disable PUSHOVER_ENABLE by setting it to False if you want to.

Node Details: The script will run on your local machine (Raspiblitz/Umbrel) or on any hosted Lightning Node with gRPC enabled and port 10009 opened. The default directories are for a Raspiblitz installation. If you want to run it remotely, you need your TLS Certificate and Admin Macaroon extracted from your Node. Put those files in a convenient location on the machine you're calling the script from and update the MACAROON_LOCATION and TLSCERT_LOCATION accordingly. Note that if you have a TLS certificate, it's probably signed against a URL, and some sites use DuckDNS for this purpose. Either way update the NODE_ADDRESS to your Node's URL. If you're running behind TOR you might need to configure further.

This will send one push notification for every Boost-A-Gram received, and by default REMEMBER_LAST_INDEX should be True. This will save a file to the same directory 

The script only looks for those TLV record IDs in the following array, but this can be updated easily as the specification changes:

TLVS = ["7629171", "7629169", "133773310"]

Set up a Cron Tab on the Blitz based on how often you want it to check. For every 5 minutes:

*/5 * * * * cd /home/admin/extractlv && /usr/bin/python /home/admin/extractlv/main.py

PUSHOVER CUSTOMISATION

Add, modify, remove those fields you want to include in the PushOver notification per below:

BOOSTAGRAM_FIELDS_TO_PUSH = ["app_name", "podcast", "episode", "message", "sender_name"]

EXTENSABILITY

The script is flexible and can extract either a matching TLV record Key-Pair or a matching TLV Key, irrespective of the Value. To extract a Boost-A-Gram it's simple:

TLVS_TO_EXTRACT = [["message", ""]]

Alternatively you could extract Action + Boost, or if you'd like, messages about the Podcast by it's name (eg Analytical) like so:

TLVS_TO_EXTRACT = [["action", "boost"], ["podcast", "Analytical"]]


WISH LIST
-------
* Summary EMail, with configurable frequency of Boost-A-Grams, as well as earning statistics



CHANGE LOG

v.0.1
-------
* Initial Release
* Supports one by one, push messaging for Boost-A-Grams via PushOver only

