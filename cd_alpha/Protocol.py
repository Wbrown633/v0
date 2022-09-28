from cd_alpha.ProtocolFactory import Step

class Protocol:
    def __init__(self, name: str) -> None:
        self.list_of_steps = []
        self.name = name
    
    def add_step(self):
        self.list_of_steps.append(Step())

    def add_step_from_json(self, json: str):
        pass

    def remove_step(self):
        pass

    def edit_step(self):
        pass
