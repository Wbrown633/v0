#!/usr/bin/python3

import io
import fcntl

__version__ = "0.1.1"

IOCTL_I2C_SLAVE = 0x0703


class Nano(object):
    """Arduino Nano object that can be read from and written to.
    Args:
        device (int): device address
        bus (int): "/dev/i2c-3" has a device address of 3
        address (int, optional): address of ioctl device slave. Default is
            IOCTL_I2C_SLAVE
    """

    def __init__(self, device, bus, address=IOCTL_I2C_SLAVE):
        self._fr = io.open(f"/dev/i2c-{str(bus)}", "rb", buffering=0)
        self._fw = io.open(f"/dev/i2c-{str(bus)}", "wb", buffering=0)
        self.d2 = False
        self.d3 = False
        self.d4 = False
        self.d5 = False

        # Set device address
        fcntl.ioctl(self._fr, address, device)
        fcntl.ioctl(self._fw, address, device)

        self.update()

    def update(self):
        """Ask Nano for status and update variables"""
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


if __name__ == "__main__":
    from time import sleep

    nn = Nano(8, 7)
    try:
        print()
        while True:
            nn.update()
            print("1 = Open     0 = Closed")
            print(
                f"D2: {int(nn.d2)}, D3: {int(nn.d3)}, D4: {int(nn.d4)}, D5: {int(nn.d5)}"
            )

            sleep(1)
    except KeyboardInterrupt as e:
        nn.close()
        print("\nFinished!")
