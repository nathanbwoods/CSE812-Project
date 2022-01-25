#
# Katherine Perry
# Computer Project #10
#
# Usage:  make -f proj11.makefile
# Makes:  proj11.client
#

proj11.client: proj11.client.o
	g++ proj11.client.o -o proj11.client

proj11.client.o: proj11.client.cpp
	g++ -Wall -c proj11.client.cpp

clean:
	rm -f proj11.client.o
	rm -f proj11.client

