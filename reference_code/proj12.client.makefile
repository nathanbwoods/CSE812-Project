#
# Katherine Perry
# Computer Project #12
#
# Usage:  make -f proj12.client.makefile
# Makes:  proj12.client
#

proj12.client: proj12.client.o
	g++ proj12.client.o -o proj12.client

proj12.client.o: proj12.client.cpp
	g++ -Wall -c proj12.client.cpp

clean:
	rm -f proj12.client.o
	rm -f proj12.client

