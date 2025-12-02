from terra_futura.interfaces import InterfacePile, InterfaceCard
from typing import Optional, Any
import json

class Pile(InterfacePile):
    _visibleCards: list[InterfaceCard]
    _hiddenCards: list[InterfaceCard]
    
    def __init__(self, all_cards: list[InterfaceCard]) -> None:
        # cards should be already shuffled
        self._hiddenCards = all_cards
        self._visibleCards: list[InterfaceCard] = []
        while len(self._visibleCards) < 4:
            self._visibleCards.insert(0, self._hiddenCards.pop()) # this way 1 is newest, 4 is oldest

        assert len(self._visibleCards) == 4

    def getCard(self, index: int) -> Optional[InterfaceCard]:
        if index not in range(1, 5):
            return None
        return self._visibleCards[index-1]

    def takeCard(self, index: int) -> None:
        selectedCard = self.getCard(index)
        if selectedCard is not None:
            self._visibleCards.remove(selectedCard)
            if len(self._hiddenCards) > 0:
                self._visibleCards.insert(0, self._hiddenCards.pop())
        return None

    def removeLastCard(self) -> None:
        self._visibleCards.pop() # remove last card
        self._visibleCards.insert(0, self._hiddenCards.pop()) # new card is interted into the first position

    def state(self) -> str:
        visible_cards_state: list[dict[str, Any]] = []
        for i, card in enumerate(self._visibleCards, start=1):
            visible_cards_state.append({
                "index": i,
                "card": card.state() if card else "None"
            })
        
        pile_state: dict[str, Any] = {
            "visible_cards": visible_cards_state,
            "hidden_cards_count": len(self._hiddenCards)
        }
        
        return json.dumps(pile_state)
