#!/usr/bin/python3

__version__ = '0.1.1'

IOCTL_I2C_SLAVE = 0x0703


class Nano(object):
    '''TESTING STUB FOR Arduino Nano object that can be read from and written to.
    Args:
        device (int): device address
        bus (int): "/dev/i2c-3" has a device address of 3
        address (int, optional): address of ioctl device slave. Default is
            IOCTL_I2C_SLAVE
    '''

    def __init__(self, device, bus, address=IOCTL_I2C_SLAVE):
        # I/O streams 
        self._fr = io.open("/dev/i2c-" + str(bus), "rb", buffering=0)
        self._fw = io.open("/dev/i2c-" + str(bus), "wb", buffering=0)
        self.d2 = False
        self.d3 = False
        self.d4 = False
        self.d5 = False

        # Set device address
        # WHILE TESTING THIS IS ONLY A LOG WRITE
        fcntl.ioctl(self._fr, address, device)
        fcntl.ioctl(self._fw, address, device)

        self.update()

    def update(self):
        '''Ask Nano for status and update variables'''
        payload = self._read(1)
        self.d2 = bool((payload[0] >> 7) & 0x01)
        self.d3 = bool((payload[0] >> 6) & 0x01)
        self.d4 = bool((payload[0] >> 5) & 0x01)
        self.d5 = bool((payload[0] >> 4) & 0x01)


    def _write(self, data: bytes):
        self._fw.write(data)

    def _read(self, noof_bytes):
        return self._fr.read(noof_bytes)

    def close(self):
        self._fw.close()
        self._fr.close()
