from cd_alpha.NewEraPumps import PumpNetwork
import serial


if __name__ == "__main__":

    WASTE_ADDR = 1
    LYSATE_ADDR = 2 

    ser =  serial.Serial ("/dev/ttyUSB0", 19200, timeout=2)
    p = PumpNetwork(ser)

    input("Connect serial cable to the PC port on the WASTE servo control board (#1) and hit ENTER.")


    print("SETTING WASTE ADR! ", p._set_addr(WASTE_ADDR))

    input("Connect serial cable to the PC port on the LYSATE servo control board (#2) and hit ENTER.")

    print("SETTING LYSATE ADR! ", p._set_addr(LYSATE_ADDR))

    input("Testing the WASTE pump, after hitting ENTER confirm that the pump moves.")

    WASTE_DIAMETER_mm = 12.45
    LYSATE_DIAMETER_mm = 12.45
    p.set_diameter(diameter_mm=WASTE_DIAMETER_mm, addr=WASTE_ADDR)
    p.set_diameter(diameter_mm=LYSATE_DIAMETER_mm, addr=LYSATE_ADDR)

    print("Rate:", p.set_rate(50.0, 'MM', WASTE_ADDR))
    print("Volume:", p.set_volume(0.5, 'ML',  WASTE_ADDR))
    print("Run:", p.run(WASTE_ADDR))

    input("Testing the LYSATE pump, after hitting ENTER confirm that the pump moves.")

    print("Rate:", p.set_rate(50.0, 'MM', LYSATE_ADDR))
    print("Volume:", p.set_volume(0.5, 'ML',  LYSATE_ADDR))
    print("Run:", p.run(LYSATE_ADDR))

