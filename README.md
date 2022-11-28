# WSPyserial

A WSPyserial é uma biblioteca para possibilitar a comunicação entre dispostivos seriais via rede utilizando o protocolo websocket.

Sua arquitetura é baseada no modelo cliente/servidor. Onde o Dispotivo serial é o servidor e qualquer cliente que conheca seu endereço e porta pode se comunicar com ele.

## Uso/Exemplos
```python
# python -m wspyserial -h
usage: __main__.py [-h] [-c] [-s] [-r] [-p PORT] [-a ADDRESS] [-d DEVICE] [-b BAUDRATE] [-v]

wspyserial - Websocket to Serial Bridge

options:
  -h, --help            show this help message and exit
  -c, --client          Run as a client
  -s, --server          Run as a server
  -r, --raw             Send raw data
  -p PORT, --port PORT  Port to listen on
  -a ADDRESS, --address ADDRESS
                        Address to connect to (default: localhost)
  -d DEVICE, --device DEVICE
                        Serial device to connect to (default: 0)
  -b BAUDRATE, --baudrate BAUDRATE
                        Baudrate to use (default: 115200)
```

#### Server - [Cmdlt, Instance and Context Manager]
```bash
 # Start a server at 8020 with command line
 python -m wspyerial -s -p 8020
```
```python
# Server as Instance
from wspyserial.server import Server
import asyncio

async def main():
    await Server("0.0.0.0", 8010, 0, 115200).run()

asyncio.run(main())
```
```python
# Server as context manager]
from wspyserial.server import Server
import asyncio

async def main():
    async with Server("0.0.0.0", 8010, 0, 115200) as server:
        await asyncio.sleep(10)

asyncio.run(main())
```
#### Client - [Cmdlt, Instance and Context Manager]
```bash
 # Connect a client on server at 0.0.0.0:8010
 python -m wspyerial -c -a 0.0.0.0 -p 8010 
```
```python
# Client as Instance
from wspyserial.client import Device as Client
from wspyserial.protocol import package
import asyncio

async def main():
    await client = Client("ws://0.0.0.0:8010")
    await client.connect()
    await client.send(package("M114 R", 2))
    await client.stop()

asyncio.run(main())
```
```python
# Client as context manager
from wspyserial.client import Device as Client
from wspyserial.protocol import package
import asyncio

async def main():
    async with Client("ws://0.0.0.0:8010") as client:
        PACKAGES = [package("G28 X", -1, 120, "ok"), package("M114 R", 2)]
        for command in PACKAGES:
            await client.send(command)

asyncio.run(main())
```