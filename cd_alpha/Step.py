class Step:
    def __init__(self, reagent: str, volume_add: float, volume_pull: float, flow_rate: float, wait_time: int) -> None:
        self.reagant = reagent
        self.volume_add = volume_add
        self.volume_pull = volume_pull
        self.flow_rate = flow_rate
        self.wait_time = wait_time