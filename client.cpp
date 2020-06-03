//
//  main.cpp
//  ball_event_prototype_client
//
//  Created by Tom Manning on 2020-04-06.
//  Copyright © 2020 Tom Manning. All rights reserved.
//

#include <iostream>

#include <grpc/grpc.h>
#include <grpcpp/channel.h>
#include <grpcpp/client_context.h>
#include <grpcpp/create_channel.h>
//#include <grpcpp/security/credentials.h>
#include <grpcpp/generic/generic_stub.h>
//#include <grpcpp/generic/async_generic_service.h>


#include "ball_event.grpc.pb.h"

using grpc::Channel;
using grpc::ClientContext;
using grpc_impl::ClientReader;
using grpc_impl::ClientReaderWriter;
using grpc_impl::ClientWriter;
using grpc::Status;

using ballevent::Point;
using ballevent::RequestEvents;
using ballevent::BallEvent;

//Point MakePoint(int32_t latitude, int32_t longitude) {
//  Point p;
//  p.set_latitudee7(latitude);
//  p.set_longitudee7(longitude);
//  return p;
//}

class BallEventClient {
public:
  BallEventClient(std::shared_ptr<Channel> channel)
  : stub_(BallEvent::NewStub(channel)) {}
  
  void GetEvents() {
    ClientContext context;
    
    RequestEvents request;
     //mode is a placeholder to start event stream, it could be config data or other parameters
    request.set_mode("getEvents");
    
    Point point;
    int32_t point_count = 0;
    
    std::unique_ptr<ClientReader<Point> > reader(
        stub_->GetEvents(&context, request));
    while (reader->Read(&point)) {
      std::cout << "Received point: " << point_count
      << "  ts: " << point.timestampms()
      << "  x: " << point.latitudee7()
      << "  y: " << point.longitudee7()
      << "  z: " << point.altitude()
      << "  type: " << point.event_type()
      << std::endl;
      point_count++;
    }
    Status status = reader->Finish();
    if (status.ok()) {
      std::cout << "GetEvents rpc succeeded." << std::endl;
    } else {
      std::cout << "GetEvents rpc failed: " << status.error_code() << std::endl;
    }
  }

private:
  std::unique_ptr<BallEvent::Stub> stub_;

}; //end of class BallEventClient

int main(int argc, const char * argv[]) {
  
  BallEventClient client( grpc::CreateChannel("localhost:50051", grpc::InsecureChannelCredentials()));
  
  client.GetEvents();

  std::cout << "Client Terminated Normally" << std::endl;;
  return 0;
}
