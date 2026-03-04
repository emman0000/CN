====================================================================
       EXPLANATION — HTTP Proxy Server (Assignment 1)
       CS3001 Computer Networks, Spring 2026
====================================================================

WHAT IS THIS?
─────────────
This project implements a simple HTTP proxy server written in C
using POSIX socket programming and process concurrency via fork().

A proxy server sits between a web browser and the destination
website. Instead of the browser communicating directly with the
website, it sends its HTTP requests to the proxy.

The proxy then:
1) Receives the request
2) Parses the target URL
3) Connects to the remote web server
4) Forwards the request
5) Relays the response back to the browser

Architecture:

    Browser  ──►  Proxy Server  ──►  Web Server
    Browser  ◄──  Proxy Server  ◄──  Web Server


SUPPORTED FEATURES
──────────────────
• Concurrent client handling using fork()
• HTTP GET request forwarding
• URL parsing (host, port, path)
• DNS resolution using gethostbyname()
• HTTP response relaying
• Basic HTTP error handling

This proxy only supports HTTP (port 80). HTTPS is not supported.


HOW TO COMPILE
──────────────

Compile the program using gcc:

    gcc proxy.c -o proxy


HOW TO RUN
──────────

Run the proxy by specifying a port number:

    ./proxy 8080

This starts the proxy server listening on port 8080.

Example output:

    Listening on port 8080...


CONFIGURING THE BROWSER
────────────────────────

Firefox:
    Settings → Network Settings → Manual Proxy Configuration

    HTTP Proxy: 127.0.0.1
    Port: 8080

Then visit a HTTP website such as:

    http://httpforever.com
    http://neverssl.com


STEP-BY-STEP CODE EXPLANATION
─────────────────────────────

1) READ COMMAND LINE ARGUMENT
   The program expects a port number when it starts.

       ./proxy 8080

   This port is converted from string to integer using atoi().


2) CREATE SERVER SOCKET
   The proxy creates a TCP socket using:

       socket(AF_INET, SOCK_STREAM, 0)

   This creates a stream socket suitable for TCP communication.


3) CONFIGURE SERVER ADDRESS
   The server address structure specifies:

       sin_family = AF_INET      → IPv4
       sin_addr = INADDR_ANY     → listen on all interfaces
       sin_port = htons(port)    → convert port to network order


4) ENABLE PORT REUSE
   setsockopt() with SO_REUSEADDR allows the proxy to reuse the
   same port even if it was recently used.


5) BIND SOCKET TO PORT
   bind() associates the socket with the chosen port so the
   operating system knows where to deliver incoming connections.


6) START LISTENING
   listen(server_fd, 10)

   This tells the OS the socket will accept incoming connections.
   Up to 10 pending connections may queue.


7) ACCEPT CLIENT CONNECTIONS
   The proxy runs an infinite loop calling accept().

       client_fd = accept(...)

   Each accept() returns a new socket for communication with
   that specific client.


8) HANDLE CONCURRENT CLIENTS USING fork()
   When a client connects, fork() creates a child process.

   Parent process:
       continues accepting new clients

   Child process:
       handles the connected client request


9) RECEIVE HTTP REQUEST
   The child process reads the HTTP request using recv().

   Example request:

       GET http://example.com/index.html HTTP/1.1
       Host: example.com


10) VALIDATE REQUEST METHOD
    The proxy checks if the method is GET.

    If not:

        HTTP/1.0 501 Not Implemented


11) PARSE THE REQUEST LINE
    The first line is parsed using sscanf():

        sscanf(buffer, "%s %s %s", method, url, version);

    Example extracted values:

        Method  → GET
        URL     → http://example.com/page
        Version → HTTP/1.1


12) EXTRACT HOST, PORT, AND PATH
    The proxy removes "http://" from the URL and separates:

        Host
        Port (default = 80)
        Path

    Example:

        URL: http://example.com/page

        Host → example.com
        Port → 80
        Path → /page


13) DNS RESOLUTION
    Domain names must be converted to IP addresses.

        gethostbyname(host)

    This resolves the hostname using DNS.


14) CONNECT TO THE REMOTE SERVER
    A new socket is created:

        remote_fd = socket(...)

    Then connect() establishes the connection:

        connect(remote_fd, ...)


15) BUILD FORWARD REQUEST
    The proxy creates a new HTTP request for the server:

        GET /page HTTP/1.0
        Host: example.com
        Connection: close

    Important difference:

        Browser → Proxy: absolute URL
        Proxy → Server: relative path


16) SEND REQUEST TO SERVER
    The proxy sends the new request using send().


17) RELAY SERVER RESPONSE
    The proxy reads the server response in chunks:

        recv(remote_fd, buffer, ...)

    Each chunk is forwarded immediately to the client:

        send(client_fd, buffer, n, 0)

    This continues until the server closes the connection.


18) CLEAN UP
    When finished:

        close(remote_fd)
        close(client_fd)

    The child process exits.


KEY NETWORKING CONCEPTS
───────────────────────

HTTP Proxy
    An intermediary that forwards HTTP requests and responses.

Sockets
    File descriptors used for network communication.

TCP
    Reliable transport protocol used by HTTP.

DNS Resolution
    Converting domain names to IP addresses.

Concurrency
    Multiple clients handled simultaneously using fork().

Absolute vs Relative URLs

    Browser → Proxy:
        GET http://example.com/page HTTP/1.1

    Proxy → Server:
        GET /page HTTP/1.0


LIMITATIONS
───────────

• Only supports HTTP (not HTTPS)
• Only supports GET requests
• No caching
• No logging
• Does not forward all headers

HTTPS would require implementing the CONNECT method and
tunneling encrypted traffic.


FILE STRUCTURE
──────────────

proxy.c
    Main proxy server implementation

README / explanation.txt
    Documentation describing the implementation
