Sure, here's a detailed pseudocode for the key components of Deno.js using WebSockets:

## Core Classes/Functions

```pseudo
class WebSocketServer:
    def __init__(self, options):
        # Initialize the WebSocket server with the given options

    def start(self):
        # Start the WebSocket server and listen for incoming connections

    def handleConnection(self, conn):
        # Handle a new WebSocket connection

    def broadcast(self, data):
        # Broadcast data to all connected clients

    def close(self):
        # Close the WebSocket server and all connections


class WebSocketClient:
    def __init__(self, url):
        # Initialize the WebSocket client with the given URL

    def connect(self):
        # Establish a WebSocket connection with the server

    def send(self, data):
        # Send data to the server over the WebSocket connection

    def receive(self):
        # Receive data from the server over the WebSocket connection

    def close(self):
        # Close the WebSocket connection


function handleWebSocketMessage(event):
    # Handle an incoming WebSocket message event
```

## Important Algorithms

```pseudo
function upgradeToWebSocket(request):
    # Perform the WebSocket handshake and upgrade the HTTP request to a WebSocket connection
    # Parse the request headers
    # Generate the WebSocket response headers
    # Send the response headers
    # Return the WebSocket connection

function parseWebSocketFrame(data):
    # Parse the incoming WebSocket frame data
    # Extract the opcode, payload length, and payload data
    # Return the parsed frame

function encodeWebSocketFrame(opcode, payload):
    # Encode the WebSocket frame with the given opcode and payload data
    # Construct the frame header
    # Append the payload data
    # Return the encoded frame
```

## Data Structures

```pseudo
struct WebSocketConnection:
    id: string
    socket: TCPSocket
    state: WebSocketState
    extensions: list<WebSocketExtension>
    subprotocols: list<string>
    sendQueue: Queue<WebSocketFrame>
    receiveQueue: Queue<WebSocketFrame>

struct WebSocketFrame:
    fin: bool
    rsv1: bool
    rsv2: bool
    rsv3: bool
    opcode: WebSocketOpcode
    payloadLength: int
    maskingKey: bytes
    payload: bytes

enum WebSocketState:
    CONNECTING
    OPEN
    CLOSING
    CLOSED

enum WebSocketOpcode:
    CONTINUATION
    TEXT
    BINARY
    CLOSE
    PING
    PONG
```

This pseudocode covers the core classes, functions, algorithms, and data structures involved in implementing a WebSocket server and client in Deno.js. The `WebSocketServer` class represents the server-side component, handling incoming WebSocket connections, broadcasting data to connected clients, and managing the WebSocket connections. The `WebSocketClient` class represents the client-side component, establishing a WebSocket connection with the server, sending and receiving data, and closing the connection.

The `upgradeToWebSocket` algorithm handles the WebSocket handshake process, upgrading an HTTP request to a WebSocket connection. The `parseWebSocketFrame` and `encodeWebSocketFrame` algorithms are responsible for parsing and encoding WebSocket frames, respectively.

The `WebSocketConnection` struct represents a WebSocket connection, containing information such as the connection ID, the underlying TCP socket, the connection state, negotiated extensions and subprotocols, and send and receive queues for WebSocket frames. The `WebSocketFrame` struct represents a WebSocket frame, containing fields such as the opcode, payload length, masking key, and payload data. The `WebSocketState` and `WebSocketOpcode` enums define the possible states and opcodes for WebSocket connections and frames, respectively.

Note that this pseudocode provides a high-level overview and may not cover all the details and edge cases involved in a production-ready implementation. Additionally, the actual implementation in Deno.js may differ slightly from this pseudocode, as it is written in TypeScript and may utilize additional libraries or frameworks.