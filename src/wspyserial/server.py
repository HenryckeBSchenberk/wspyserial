
from uuid import uuid4
from .device import Device
from .protocol import package as pkg
from os import environ
import json
import websockets
from threading import Event
import asyncio

class Server():
    def __init__(self, host, port, device, baudrate, loop=None, force_create=False):
        self._id= uuid4().hex
        self.host = host
        self.port = port
        self.stopped = Event()
        self.running = Event()
        self.loop = loop or asyncio.get_event_loop()
        self._async_stopped = self.loop.create_future()
        self._async_started = self.loop.create_future()
        self._async_stopped.add_done_callback(self.stop_callback)
        self.serve = websockets.serve(self.handler, self.host, self.port)
        self.SERIAL = Device(device_id=device, baudrate=baudrate, force_create=force_create)

    async def __aenter__(self):
        return await self.serve.__aenter__()

    async def __aexit__(self, *args):
        await self.serve.__aexit__(*args)
        self.SERIAL.stop()
    
    def stop_callback(self,result):
        self.stopped.set()

    async def run(self):
        try:
            async with self.serve:
                await self._async_stopped
        except KeyboardInterrupt:
            pass

    def stop(self):
        self._async_stopped.set_result('Exit')
        self.stopped.wait()

    def unpacking(self, message):
        return pkg(**json.loads(message))
    
    def packing(self, _id, message):
        if isinstance(_id, pkg):
            _id = _id._id
        return json.dumps({"_id":_id,"data":message})
        
    def read(self, _id, event):
        return self.SERIAL.read(_id, event, 2)

    def send(self, package):
        return self.SERIAL.send(package)

    async def handler(self, websocket):
        try:
            async for message in websocket:
                package = self.unpacking(message)
                reference = self.send(package)
                if package.read:
                    response = self.read(*reference)
                    await websocket.send(self.packing(package, response))
        except websockets.ConnectionClosed:
            print('Connection closed', websocket)
            pass

async def main(host, port, device, baudrate, force_create=False):
    return await Server(host, port, device, baudrate,force_create).run()

if __name__ == '__main__':
    
    HOST = environ.get("SERVER_HOST", "0.0.0.0")
    PORT = environ.get("SERVER_PORT", 8010)
    DEVICE_ID = environ.get("DEVICE_ID", 0)
    BAUDRATE = environ.get("BAUDRATE", 115200)
    FORCE_SERIAL= environ.get("FAKE_SERIAL", False)

    asyncio.run(main(HOST, PORT, DEVICE_ID, BAUDRATE, FORCE_SERIAL))
