# CS 2620 Chat Application

A real-time chat application built in Python using **gRPC** and **Tkinter** for the GUI.  
This application supports **multiple clients** and allows users to send and receive messages through a centralized server. It supports adding replica servers, making it crash fault tolerant.

## Usage

1. Configure PYTHONPATH and pip install pytest:

    Navigate to `262-Design-Exercise-4` directory.

    ```bash
    pip install pytest
    export PYTHONPATH="$PWD"
    ```

2. Start the server:

    ```bash
    python server/server_proto.py --port <port number>
    ```

    --is-leader (store true): Flag to indicate server is running as leader.
    --port: Port server listens to.
    --hi: Heart beat check interval.
    --leader-address: `IP:SOCK` of leader address.

3. Start a client:

    ```bash
    python client/client_proto.py --server-ip <server ip address> --poll-frequency <frequency to poll the server for messages>
    ```

    --server-address: The leader server’s IP address.
    --poll-frequency (Optional): How often the client polls for new messages (default: 10000ms).

Type `exit` to close the client.

4. Configuration

The config.ini file stores default settings:

```
[network]
host = 0.0.0.0
port = 60000
use_wire_protocol = True
```

5. Proto file generation

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. chat.proto
```
