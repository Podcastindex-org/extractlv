# extractlv
Tools for extracting TLV's from a lightning node and doing cool things with them.

INSTALLATION INSTRUCTIONS

Raspiblitz should already have installed:
- grpcio (old version) Upgrade to latest:
    - pip3 install --upgrade grpcio
- googleapis-common-protos (already installed)

pip3 install grpcio-tools

git clone https://github.com/googleapis/googleapis.git

curl -o lightning.proto -s https://raw.githubusercontent.com/lightningnetwork/lnd/master/lnrpc/lightning.proto

python -m grpc_tools.protoc --proto_path=googleapis:. --python_out=. --grpc_python_out=. lightning.proto


CHANGE LOG

v.0.1
-------
* Initial Release
* TBD

