Sure, here's some pseudocode for key components of using WebSockets in Rust, including core classes/functions, important algorithms, and data structures. Please note that this is a high-level overview, and you may need to consult the official Rust and WebSocket crate documentation for more detailed implementation.

## Core Classes/Functions

### WebSocket Server

```rust
struct WebSocketServer {
    // Server configuration
    address: SocketAddr,
    // WebSocket connections
    connections: Vec<WebSocketConnection>,
}

impl WebSocketServer {
    fn new(address: SocketAddr) -> WebSocketServer {
        WebSocketServer {
            address,
            connections: Vec::new(),
        }
    }

    fn run(&mut self) {
        // Start the WebSocket server
        let server = WebSocket.bind(self.address).unwrap();

        // Handle incoming connections
        for connection in server.incoming() {
            let mut conn = connection.unwrap();

            // Handle WebSocket handshake
            if conn.handshake().is_ok() {
                self.connections.push(conn);
            }
        }
    }

    fn broadcast(&mut self, message: &str) {
        // Send a message to all connected clients
        for conn in &mut self.connections {
            conn.send_message(message).unwrap();
        }
    }
}
```

### WebSocket Client

```rust
struct WebSocketClient {
    // WebSocket connection
    connection: WebSocketConnection,
}

impl WebSocketClient {
    fn new(url: &str) -> WebSocketClient {
        let connection = WebSocket.connect(url).unwrap();
        WebSocketClient { connection }
    }

    fn send_message(&mut self, message: &str) {
        self.connection.send_message(message).unwrap();
    }

    fn receive_message(&mut self) -> String {
        self.connection.receive_message().unwrap()
    }
}
```

## Important Algorithms

### WebSocket Handshake

The WebSocket handshake is a crucial step in establishing a WebSocket connection. It involves exchanging HTTP headers between the client and server to upgrade the connection from HTTP to WebSocket protocol. The handshake algorithm typically follows these steps:

1. Client sends a WebSocket handshake request with specific headers (`Upgrade`, `Connection`, `Sec-WebSocket-Key`, etc.).
2. Server validates the request headers and generates a response with a `Sec-WebSocket-Accept` header based on the client's `Sec-WebSocket-Key`.
3. If the handshake is successful, the connection is upgraded to the WebSocket protocol, and data can be exchanged bidirectionally.

### WebSocket Message Framing

WebSocket messages are transmitted in frames, which consist of a header and payload data. The message framing algorithm involves:

1. Determining the frame opcode (text, binary, control, etc.).
2. Calculating the payload length and encoding it in the frame header.
3. Applying masking (for client-to-server frames) or unmasking (for server-to-client frames) to the payload data.
4. Transmitting the frame header and payload data over the WebSocket connection.

## Data Structures

### WebSocket Connection

The `WebSocketConnection` struct represents a single WebSocket connection between the client and server. It typically contains information such as:

```rust
struct WebSocketConnection {
    // TCP socket
    socket: TcpStream,
    // WebSocket handshake details
    handshake: WebSocketHandshake,
    // Incoming message buffer
    incoming_buffer: Vec<u8>,
    // Outgoing message buffer
    outgoing_buffer: Vec<u8>,
}
```

### WebSocket Message

The `WebSocketMessage` struct represents a WebSocket message, which can be either text or binary data. It may contain fields such as:

```rust
struct WebSocketMessage {
    // Message opcode (text, binary, control, etc.)
    opcode: u8,
    // Message payload data
    payload: Vec<u8>,
    // Message metadata (optional)
    metadata: HashMap<String, String>,
}
```

These are just examples, and the actual implementation may vary depending on the WebSocket crate you're using in Rust. Additionally, you may need to handle other aspects such as connection management, error handling, and performance optimizations.