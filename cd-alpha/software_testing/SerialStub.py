import logging

class SerialStub:
    '''Stub for testing GUI and other Unit Testing use only. Doesn't communicate with anything'''
    
    def readline(self):
        return ""

    def write(self, write_string):
        pass