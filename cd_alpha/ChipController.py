from dataclasses import dataclass

from cd_alpha.Protocol import Protocol


@dataclass
class ChipController:
    protocol: Protocol

    def next(self):
        '''Advance iterator to the next step in the protocol.'''
        pass
