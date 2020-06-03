# temp-development-examples

The files in this repository are:
1. an example gRPC proto file showing possible message content
2. a simple gRPC client written in C++ which recieves message defined by the proto file and just prints the messages out
3. a gRPC server written in Python that reads content for ball event messages from a CSV file and sends them to a client.

This code was used to test sending ball event messages from a macBook running the python gRPC server to a RPi running the C++ gRPC client.
