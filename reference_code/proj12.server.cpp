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

#define BSIZE 4096

int main( int argc, char* argv[] )
{
    char hostName[16];
	unsigned int portNumber;
    
    // Create a socket
    int sockfd = socket( AF_INET, SOCK_STREAM, 0 );
    if (sockfd < 0) 
    {
        perror( "socket" );
        exit( 2 );
    }

    // Bind it to a port
    struct sockaddr_in saddr;
    bzero( &saddr, sizeof(saddr) );
    saddr.sin_family = AF_INET;
    saddr.sin_port = htons( 0 );
    saddr.sin_addr.s_addr = htonl( INADDR_ANY );
    

    int bstat = bind( sockfd, (struct sockaddr *) &saddr, sizeof(saddr) );
    if (bstat < 0)
    {
        perror( "bind" );
        exit( 3 );
    }
    // Get the host and port
    struct sockaddr_in my_addr;
    bzero(&my_addr, sizeof(my_addr));
	int len = sizeof(my_addr);
	getsockname(sockfd, (struct sockaddr *) &my_addr, (socklen_t*)&len);
    inet_ntop(AF_INET, &my_addr.sin_addr, hostName, sizeof(hostName));
	portNumber = ntohs(my_addr.sin_port);

    gethostname(hostName, 16);
    cout << hostName << " " << portNumber << endl << endl << endl;

    // Listen for a connection
    int lstat = listen( sockfd, 1 );
    if (lstat < 0)
    {
        perror( "listen" );
        return 0;
    }

    struct sockaddr_in caddr;
    unsigned int clen = sizeof(caddr);
     bzero( &caddr, sizeof(caddr) );

    int sd_client = accept( sockfd, (struct sockaddr *) &caddr, &clen );
    if (sd_client < 0)
    {
        perror( "accept" );
        return 0;
    }
    
    struct hostent *host_info = gethostbyaddr(
      (const char *) &caddr.sin_addr.s_addr,
      sizeof(caddr.sin_addr.s_addr), AF_INET);

    if (host_info == NULL)
    {
      perror( "gethostbyaddr" );
      exit( 6 );
    }

    char * host = inet_ntoa( caddr.sin_addr );
    if (host == NULL)
    {
      perror( "inet_ntoa" );
      exit( 7 );
    }

    // Wait for client to send filename
    char filename1[BSIZE];

    bzero( filename1, BSIZE );
    int nrecv = recv( sd_client, filename1, BSIZE, 0 );
    if (nrecv < 0) 
    {
        perror( "recv" );
        return 0;
    }

    // Open the file, check for errors
    int openSuccess1 = open( filename1, O_RDONLY );
    char failmsg[10] = "FAILED";
    char openmsg[10] = "OPEN";
    if (openSuccess1 == -1)
    {
        perror("Error opening file.\n");
        send( sd_client, failmsg, 10, 0 );
        return 0;
    }
    send( sd_client, openmsg, 10, 0 );
    
    char msg[BSIZE];
    string sendmsg = "SEND";
    recv(sd_client, msg, BSIZE, 0);

    // read in file and error check
    char file1[64];
    ssize_t bytes = read(openSuccess1, file1, 64);
    if (bytes == -1)
    {
        perror("Error reading from file.\n");
        return 0;
    }

    // loop over file1 contents while more remains, and send to client
    while (bytes != 0)
    {
        send( sd_client, file1, bytes, 0 );
        bzero( file1, 64 );
        bytes = read(openSuccess1, file1, 64);
        recv(sd_client, msg, BSIZE, 0);
    }

    close( sockfd );
    close(openSuccess1);
   
    return 0;
}


