import logging

class PumpNetwork:
    '''TESTING STUB FOR LOCAL GUI DEVELOPMENT. DOES NOT COMMUNICATE WITH PUMP NETWORK'''

    logging.warning('*** USING TEST STUB WILL NOT COMMUNICATE WITH PUMPS ***')
    FLOW_RATE_UNITS = ['MM', 'MH', 'UM', 'UH', '']  # MM=ml/min, MH=ml/hr, UH=μl/hr, UM=μl/min


    def __init__(self, ser, max_noof_retries=3):
        self.ser = ser
        self.safe_protocol = False
        self.max_noof_retries = max_noof_retries


    def _get_response(self):
        output = []
        first_char = self.ser.readline(1)
        #if first_char != b'\x02':
        #    raise IOError('Not correctly formated response. First character was {:}, expected 0x02'.format(first_char))
        #while True:
        #    c = self.ser.readline(1)
        #    if c == b'\x03': break  # ETX (End of text). Stop looking for response characters.
        #    elif c == '':
        #        raise IOError('Response read timed out')
        #    output.append(c.decode('utf8'))
        response = "".join(output)
        logging.debug(f"NEP: Got response: {response}")
        return response


    def _send_command(self, cmd_str, addr=''):
        tmp = '{0}{1}\r'.format(addr, cmd_str)
        logging.debug(f"NEP: Sending comand: {tmp}")
        for n in range(self.max_noof_retries + 1):
            try:
                self.ser.write(str.encode(tmp))
                response = self._get_response()
                if '?' in response:
                    msg_str = "Error in response from network. Response: {}".format(response)
                    raise IOError(msg_str)
                else:
                    return response
            except:
                if n >= self.max_noof_retries:
                    logging.error("NEP: Maximum number of tries reached for sending command.")
                    raise


    def run(self, addr=''):
        return self._send_command('RUN', addr)


    def purge(self, direction=1, addr=''):
        if direction == 1:
            direction_str = "INF"
        elif direction == -1:
            direction_str = "WDR"
        self._send_command('VOL0', addr)
        #TODO Create self._set_dir(dir=1[-1]) function
        resp_dir = self._send_command('DIR {:}'.format(direction_str), addr)
        resp_pur = self._send_command('PUR', addr)
        return resp_dir, resp_pur


    def stop(self, addr=''):
        return self._send_command('STP', addr)


    def set_diameter(self, diameter_mm, addr=''):
        return self._send_command('DIA{:0.2f}'.format(diameter_mm), addr)


    def set_rate(self, rate, unit, addr=''):
        flow_rate = float(rate)
        if unit not in PumpNetwork.FLOW_RATE_UNITS:
            raise TypeError('Flow rate unit {} is not i list among the allowed units: [{}]'.format(unit, ', '.join(FLOW_RATE_UNITS)))
        # TODO Add checks of ranges
        direction = 'INF'
        if flow_rate < 0: direction = 'WDR'
        resp_dir = self._send_command("DIR{:}".format(direction), addr)
        resp_rate = self._send_command("RAT{:.0f}{:}".format(abs(flow_rate), unit), addr)
        return resp_dir, resp_rate

    def set_volume(self, volume, unit, addr=''):
        #TODO: Add checks, volume cannot be larger than 99
        resp_unit = self._send_command("VOL{:}".format(unit), addr)
        resp_vol = self._send_command("VOL{:5.3f}".format(volume), addr)
        return resp_vol, resp_unit


    # def get_volume_status(self, addr=''):
    #     response = self._send_command("DIS", addr)
    #     resp_addr = response[0:2]
    #     resp_dir = response[2]
    #     resp_vols = response[3:-2]
    #     resp_unit = response[-2:]
    #     # print(resp_addr)
    #     # print(resp_dir)
    #     # print(resp_vols)
    #     # print(resp_unit)
    #     match = re.match(r"([a-z]+)([0-9]+)", resp_vols, re.I)
    #     if match:
    #         items = match.groups()
    #         print(items)

    #     return response

    # Status stub
    def status(self, addr=''):
        response = self._send_command("", addr)
        # resp_addr = int(response[0:2])
        #current_status = response[2]
        current_status = "S"
        return current_status


    def get_volume_ml(self, addr=''):
        response = self._send_command("VOL", addr)
        return response


    def _set_addr(self, addr):
        logging.warning(f"NEP: Setting addr of *ALL* connected pumps to {addr:02}")
        return self._send_command("ADR{}".format(addr), addr='*')

    def buzz(self, addr='', repetitions=1):
        return self._send_command("BUZ 1 {:}".format(int(repetitions)), addr)
    
    def stop_all_pumps(self, list_of_pumps=[1,2]):
        logging.debug("CDA: Stopping all pumps.")
        for addr in list_of_pumps:
            try:
                self.stop(addr)
            except IOError as err:
                if str(err)[-3:] == "?NA":
                    logging.debug(f"CDA: Pump {addr:02} already stopped.")
                else:
                    raise        

    

