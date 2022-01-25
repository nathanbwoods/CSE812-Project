/****************************************************************************
  Katherine Perry
  Computer Project #12
****************************************************************************/
#include <string.h>
#include <iostream>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h> 
#include <arpa/inet.h>

using namespace std;



int main( int argc, char* argv[] )
{
    
    char* hostName = nullptr;
    int portNumber = 0;
    char* filename = nullptr;
    if (argc != 4) 
    {
        cerr << "Must supply three arguments.\n";
        return 0;
    }
    filename = argv[3];
    portNumber = stoi(argv[2]);
    hostName = argv[1];

    // Start socket
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
    {
        cerr << "Socket failed.\n";
        return 0;
    }
    
    // Set address details of remote server
    struct hostent * server = gethostbyname( hostName );
    if (server == NULL)
    {
        cerr << "Error: no such host " << hostName << endl;
        return 0;
    }

    struct sockaddr_in serv_addr;
    bzero( &serv_addr, sizeof(serv_addr) );
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons( portNumber );
    bcopy( server->h_addr, &serv_addr.sin_addr.s_addr, server->h_length );

    // Connect to remote server with given host and port
    int connection = connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr));
    if (connection < 0)
    {
        cerr << "Connection failed.\n";
        return 0;
    }


    // Send the file name, check for errors
    int sendSuccess = send(sockfd, filename, strlen(filename), 0);
    if (sendSuccess == -1)
    {
        cerr << "Error sending file.\n";
        return 0;
    }
    char openBuffer[100];
    string failed = "FAILED";
    char sendmsg[10] = "SEND";
    recv(sockfd, openBuffer, 100, 0);

    if (openBuffer == failed)
    {
        cerr << "Failed to open file.\n";
        return 0;
    }
    send(sockfd, sendmsg, sizeof(sendmsg), 0);

    // read in file and error check
    char buf[64];
    ssize_t bytes = recv(sockfd, buf, 64, 0);
    if (bytes == -1)
    {
        cerr << "Error reading from file.\n";
        return 0;
    }

    // loop over received file contents while more remains, and write to output
    while (bytes > 0)
    {
        write(1, buf, bytes);
        send(sockfd, sendmsg, sizeof(sendmsg), 0);
        bytes = recv(sockfd, buf, 64, 0);
    }
    cout << endl;
   
    return 0;
}


