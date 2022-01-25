#
# Katherine Perry
# Computer Project #12
#
# Usage:  make -f proj12.server.makefile
# Makes:  proj12.server
#

proj12.server: proj12.server.o
	g++ proj12.server.o -o proj12.server

proj12.server.o: proj12.server.cpp
	g++ -Wall -c proj12.server.cpp

clean:
	rm -f proj12.server.o
	rm -f proj12.server

