# Supports a client connecting with a stream request and generates a stream of events using a CSV file

from concurrent import futures
import time
import logging
import sys
import grpc
from google.protobuf.timestamp_pb2 import Timestamp

import ball_event_pb2
import ball_event_pb2_grpc
import ball_event_resources

class BallEventServicer(ball_event_pb2_grpc.BallEventServicer):
    # num_rpc_getEvents = 0

    def __init__(self, input_csv):
        self.db = ball_event_resources.read_database(input_csv)
        self.num_rpc_getEvents = 0
        self.num_streamed_ball_events = 0

    @property
    def num_rpc_getEvents(self):
        return self.num_rpc_getEvents
    @num_rpc_getEvents.setter
    def num_rpc_getEvents(self, value):
        self._num_rpc_getEvents = value


    def GetEvents(self, request, context):
        logging.debug(" Handling GetEvents RPC.")
        # self.num_rpc_getEvents += 1
        point = ball_event_pb2.Point()
        previous_ts = None
        for row in self.db:
            if previous_ts == None:
                seconds_till_next_event = 0
            else:
                seconds_till_next_event = (int(row['timestampMs'])-previous_ts)/1000
            previous_ts = int(row['timestampMs'])
            time.sleep(seconds_till_next_event)
            for key, value in row.items():
                point.__setattr__(key, int(value))
            # use a real (current) timestamp in event; timestamp will reflect inter-event delays
            point.timestampMs = int(time.time() * 1000)
            # self.num_streamed_ball_events += 1
            yield point

def serve(port, input_csv):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ball_event_pb2_grpc.add_BallEventServicer_to_server(
        BallEventServicer(input_csv), server)
    server.add_insecure_port('[::]:'+port)
    server.start()
    # print(f"dir: {dir(ball_event_pb2_grpc.BallEventServicer)}")
    # print(f"RPC calls: {ball_event_pb2_grpc.BallEventServicer.__getattribute__('get_num_rpc_getEvents')}")
    # print(f"RPC calls: {ball_event_pb2_grpc.BallEventServicer.num_rpc_getEvents}")
    logging.info(f' -- Server listening on port: {port}; using events from file: {input_csv} --')
    try:
        server.wait_for_termination()
    except (KeyboardInterrupt, SystemExit):
        logging.info(" -- Exiting due to keyboard interrupt or System Exit --")
        sys.exit()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Ball Location Event Server')
    parser.add_argument('-l', '--loglevel', default="INFO", help=': INFO, DEBUG, WARNING', required=False)
    parser.add_argument('-p', '--port', default="50051", help=': IP port for the server to listen on', required=False)
    parser.add_argument('-i', '--input_file', default="ball_events.csv",
                        help=': filename of the CSV file containing ball location events',
                        required=False)
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.loglevel))
    serve(args.port, args.input_file)
