import unittest
from src.wspyserial.device import Device
from src.wspyserial.protocol import package as pkg
import uuid
import random


class Serial_Hardware(unittest.TestCase):
    @classmethod
    def setUpClass(cls):    
        device = Device()
        cls.serial = device

    def test_wrong_data(self):
        with self.assertRaises(TypeError):
            self.serial.send('Não é um pkg', read=True)

    def test_send_and_recive(self):
        commands = [pkg('G0 X0 Y0 F0', read = False), pkg('M114 R', 2)]
        for command in commands:
            self.serial.send(command)
        data = self.serial.read(commands[1]._id, commands[1].event, 2)
        self.assertEqual(data, ['X:0.00 Y:0.00 Z:0.00 E:0.00 Count X:0 Y:0 Z:0', 'ok'])

    def test_multiple_results(self):
        commands = []
        for _ in range(0, 100):
            _id = uuid.uuid4().hex
            read = bool(random.getrandbits(1))
            commands.append(pkg(f'M118 {_id}',2, _id=_id, read=read))

        for A in commands:
            self.serial.send(A)
        
        commands = list(filter(lambda x: (x.read == True), commands))
        for A in commands:
            data = self.serial.read(A._id, A.event, 3)
            self.assertEqual(data, [A._id, 'ok'])

                
    @classmethod
    def tearDownClass(cls):
        cls.serial.stop()


if __name__ == '__main__':
    unittest.main()
