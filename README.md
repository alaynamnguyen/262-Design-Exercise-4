# CS 2620 Chat Application

A real-time chat application built in Python using **sockets** and **Tkinter** for the GUI.  
This application supports **multiple clients** and allows users to send and receive messages through a centralized server.

## Usage

1. Configure PYTHONPATH and pip install pytest:

    Navigate to `262-Design-Exercise-2` directory.

    ```bash
    pip install pytest
    export PYTHONPATH="$PWD"
    ```

2. Start the server:

    ```bash
    python server/server_proto.py
    ```

3. Start a client:

    ```bash
    python client/client_proto.py --server-ip <server ip address> --poll-frequency <frequency to poll the server for messages>
    ```

    --server-ip (Optional): The server’s IP address. Defaults to config.ini.
    --poll-frequency (Optional): How often the client polls for new messages (default: 10000ms).

Type `exit` to close the client.

4. Configuration

The config.ini file stores default settings:

```
[network]
host = 0.0.0.0
port = 65433
use_wire_protocol = True
```
