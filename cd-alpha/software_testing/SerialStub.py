import logging

class SerialStub:
    '''Stub for testing GUI and other Unit Testing use only. Doesn't communicate with anything'''

    def readline(self, lines):
        logging.warning('STUB USED FOR SERIAL COMMUNICATION, CANNED ANSWER PROVIDED FOR READ')
        return b'\x02' 

    def write(self, write_string):
        logging.warning('String: {} was written'.format(write_string))

    def close(self):
        logging.info('CLOSING SERIAL STUB')