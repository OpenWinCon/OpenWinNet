# Copyright 2015, Google Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.



from concurrent import futures
import time

import grpc
.
import device_config_pb2
import device_config_pb2_grpc

from hostapd import hostapd

_ONE_DAY_IN_SECONDS = 60 * 60 * 24




class Configurer(device_config_pb2_grpc.DeviceConfigServicer):

    def __init__(self):
        self.ap = device_config_pb2.Devices.AccessPoint.Ap()
        self.hostap = hostapd(self)

    def on_ap_changed(self, param):
        for key, val in param.items():
            if hasattr(self.ap, key):
                setattr(self.ap, key, val)



    def Hello(self, request, context):
        print("-------------------------")
        print("Received Hello Request")
        print("-------------------------")
        return device_config_pb2.HelloResponse(
            ip=self.ap.ip,
            power_on_off=self.ap.power_on_off,
            ssid=self.ap.ssid,
            channel = self.ap.channel,
            hw_mode = self.ap.hw_mode,
            password = self.ap.password
        )


    def EditConfig(self, request, context):

        print("-------------------------")
        print("Received Edit-config Request")
        print("command: " + request.command + " value: " + request.value)
        print("-------------------------")


        self.hostap._edit_config(request.command, request.value)

        return device_config_pb2.EditConfigResponse(
            power_on_off=self.ap.power_on_off,
            ssid=self.ap.ssid,
            channel=self.ap.channel,
            hw_mode=self.ap.hw_mode,
            password=self.ap.password
        )

    def GetConfig(self, request, context):
        print("-------------------------")
        print("Received Get-config Request")
        print("-------------------------")

        return device_config_pb2.GetConfigResponse(
            ip=self.ap.ip,
            power_on_off=self.ap.power_on_off,
            ssid=self.ap.ssid,
            channel=self.ap.channel,
            hw_mode=self.ap.hw_mode,
            password=self.ap.password
        )

'''
  def SayHello(self, request, context):
    return helloworld_pb2.HelloReply(message='Hello, %s!' % request.name)
'''

def serve():

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    device_config_pb2_grpc.add_DeviceConfigServicer_to_server(Configurer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
