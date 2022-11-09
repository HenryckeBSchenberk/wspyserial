import asyncio
from multiprocessing.connection import Client
import unittest

from src.wspyserial.client import Device as Client
from src.wspyserial.server import Server
from src.wspyserial.protocol import example_packages

def chunk_list(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

class Serial_Service(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.loop = loop
        self.host = '0.0.0.0'    
        self.port = '8010'
        self.uri = f'ws://{self.host}:{self.port}'
        self.baudrate = 115200
        self.device = '0'
        self.server = Server(self.host, self.port, self.device, self.baudrate, self.loop)
        self.package_amount = 20
        self.clients = 2

    async def runner(self, *courotines):
        async with self.server:
            await asyncio.gather(*courotines)


    def test_ws_integrity(self):
        async def validate():
            package_list = example_packages(self.package_amount)
            # Connect to the server with an client
            async with Client(self.uri) as client:
                #Store all received values
                echos = [await client.send(package) for package in package_list]
                # Compare anser and 
                for get, post in zip(echos, package_list):
                    if post.read:
                        self.assertTrue(post._id == get._id == get.data[0])

        workers = [validate() for _ in range(self.clients)]
        run = self.runner(*workers)
        self.loop.run_until_complete(run)

if __name__ == '__main__':
    unittest.main()