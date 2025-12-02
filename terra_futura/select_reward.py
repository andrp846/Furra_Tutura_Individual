from .simple_types import Resource
from .interfaces import InterfaceSelectReward, InterfaceCard
from typing import List, Optional

class SelectReward(InterfaceSelectReward):
    _player: Optional[int]
    _selection: list[Resource]
    _card: Optional[InterfaceCard]

    @property
    def player(self) -> int:
        if self._player is None:
            raise ValueError("Player not set")
        return self._player
    
    def __init__(self) -> None:
        self._player: Optional[int] = None           # The assisting player who gets the reward
        self._selection: List[Resource] = []         # Available resources to choose from (paid by active player)
        self._card: Optional[InterfaceCard] = None   # The assisting player's card where reward will be placed
    
    def setReward(self, player: int, card: InterfaceCard, reward: List[Resource]) -> None:
        self._player = player
        self._card = card
        self._selection = reward.copy()
    
    def canSelectReward(self, resource: Resource) -> bool:
        if self._card is None:
            return False

        if self._player is None:
            return False

        if not self._card.canPutResources([resource]):
            return False

        if resource not in self._selection:
            return False
        return True

    def selectReward(self, resource: Resource) -> None:
        if not self.canSelectReward(resource):
            raise ValueError("Resource not available for selection")
        
        self._selection.remove(resource)
        
        if self._card is not None:
            self._card.putResources([resource])

    def state(self)-> str:
        resources_str = ', '.join([f'"{r.name}"' for r in self._selection])
        return f'{{"player": {self._player}, "available_resources": [{resources_str}]}}'