#include<stdio.h>
#include<stdlib.h> //atoi convert string to interger
#include<unistd.h> //for fork()
#include<string.h> //for parsing
#include<arpa/inet.h> // for socket , bind , htons
#include<netdb.h>

/*
Create socket
Bind to port
Listen
Wait
Accept client
Print message
Close client
Repeat forever

*/

int main(int argc, char *argv[]){
//Check if port was given
    if(argc != 2){
        printf("Usage: %s <port>\n", argv[0]);
        return 1;
    }
//Convert Port to Integer
    int port = atoi(argv[1]);

    int server_fd , client_fd;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len = sizeof(client_addr);


    //1.Socket created
    //Sock Stream - TCP
    // 0 default TCP 
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if(server_fd < 0) {
        perror("Socket creation failed");
        return 1;
    }

     int opt = 1;
     setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    //2.Address Structure
    server_addr.sin_family = AF_INET;//IPv4
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);//converts port number to network format

    //3.Bind Socket
    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr))<0){
        perror("Bind failed");
        return 1;
    }

    //4.Listen
    if(listen(server_fd, 10)<0){
        perror("Listen failed");
        return 1;
    }

    printf("Listening on port %d...\n", port);

    while(1){

        client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &client_len);
        if(client_fd < 0){
            perror("Accept failed");
            continue;
        }
        printf("Client connected \n");

        int pid = fork();

        if (pid < 0){
            perror("Fork Failed");
            close(client_fd);
            continue;
        }

        if (pid == 0){
        //Child Process
           

        close(server_fd);  // child does not listen
        
        printf("Child handling client\n");

        char buffer[4096];
        int bytes_received = recv(client_fd, buffer, sizeof(buffer) - 1, 0);
         
        if (bytes_received <= 0) {
            close(client_fd);
            exit(0);
        }

        buffer[bytes_received] = '\0';

            printf("Request received:\n%s\n", buffer);

            // Validate GET method
            if (strncmp(buffer, "GET", 3) != 0) {
                char *response =
                    "HTTP/1.0 501 Not Implemented\r\n"
                    "Content-Type: text/plain\r\n"
                    "\r\n"
                    "501 Not Implemented\n";

                send(client_fd, response, strlen(response), 0);
                close(client_fd);
                exit(0);
        
    }

    // Parse request line
       char method[16], url[2048], version[16];
            sscanf(buffer, "%s %s %s", method, url, version);

            printf("Method: %s\n", method);
            printf("URL: %s\n", url);
            printf("Version: %s\n", version);

         // Remove "http://"
            char *url_ptr = url;

            if (strncmp(url_ptr, "http://", 7) == 0) {
                url_ptr += 7;
            }

            // Separate host and path
            char *path = strchr(url_ptr, '/');

            if (path != NULL) {
                *path = '\0';
                path++;
            } else {
                path = "";
            }

            // Extract port if exists
            char host[1024];
            int remote_port = 80;  // default HTTP port

            char *port_ptr = strchr(url_ptr, ':');

            if (port_ptr != NULL) {
                *port_ptr = '\0';
                port_ptr++;
                remote_port = atoi(port_ptr);
            }
             strcpy(host, url_ptr);

             //COnnect to remote server 

             int remote_fd;
             struct hostent *remote_host;
             struct sockaddr_in remote_addr;

             remote_fd = socket(AF_INET, SOCK_STREAM, 0);
             if(remote_fd < 0){
                perror("Remote socket failed");
                close(client_fd);
                exit(1);
             }

             remote_host = gethostbyname(host);
             if(remote_host == NULL){
                perror("DNS resolution failed");
                close(remote_fd);
                close(client_fd);
                exit(1);
             }

             remote_addr.sin_family = AF_INET;
             remote_addr.sin_port = htons(remote_port);
             memcpy (&remote_addr.sin_addr, remote_host->h_addr, remote_host->h_length);

             if(connect(remote_fd, (struct sockaddr *)&remote_addr, sizeof(remote_addr))<0){
                perror("Conncet to remote failed");
                close(remote_fd);
                close(client_fd);
                exit(1);

             }

             //Send request to remote server 

             char request[4096];
             snprintf(request, sizeof(request),
                "GET /%s HTTP/1.0\r\n"
                "Host: %s\r\n"
                "Connection: close\r\n"
                "\r\n",
                path, host
            );

            send(remote_fd, request, strlen(request), 0);

            //Relay response back to client
            int n;
            while ((n = recv(remote_fd, buffer, sizeof(buffer), 0)) > 0) {
                send(client_fd, buffer, n, 0);
            }
             printf("Parsed Results:\n");
            printf("Host: %s\n", host);
            printf("Port: %d\n", remote_port);
            printf("Path: /%s\n", path);

            close(remote_fd);
            close(client_fd);
            exit(0);
        }
    
        
            


        else{
            //Parent 
            close(client_fd);
        }//end else 
      


    }//end while 
    close(server_fd); //will not actually execute 
    return 0;
}
    
