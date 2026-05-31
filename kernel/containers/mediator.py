from abc import ABC, abstractmethod


class NeuroFuzzyMediator(ABC):
    @abstractmethod
    def notify(self, sender: 'NeuroFuzzyComponent', event: str, index=None):
        pass

class NeuroFuzzyComponent:
    def __init__(self, mediator: NeuroFuzzyMediator = None):
        self._mediator = mediator
