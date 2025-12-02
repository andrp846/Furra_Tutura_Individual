from unittest.mock import Mock
from terra_futura.game import Game
from terra_futura.simple_types import Deck, GridPosition
from terra_futura.select_reward import SelectReward
from terra_futura.interfaces import InterfaceCard
from terra_futura.pile import Pile
from typing import cast

class TestPile:
    def test_pile_initialization(self) -> None:
        """Test that a pile is initialized correctly"""
        card = Mock(spec=InterfaceCard)
        pile = Pile(all_cards=[card for _ in range(10)])
        assert pile.getCard(1) == card
        assert pile.getCard(2) == card
        assert pile.getCard(4) == card
        # 4 visible cards
        assert pile.getCard(5) is None
        assert pile.getCard(10) is None
    
    def test_take_card(self) -> None:
        """Test that takeCard is called correctly"""
        pile_mock = Pile([Mock(spec=InterfaceCard) for _ in range(10)])
        assert pile_mock.getCard(1) != pile_mock.getCard(2)  # Ensure different cards
        card_before = pile_mock.getCard(1)
        pile_mock.takeCard(1)
        assert pile_mock.getCard(1) != card_before

    def test_remove_last_card(self) -> None:
        """Test that removeLastCard works correctly"""
        my_cards = [Mock(spec=InterfaceCard) for _ in range(10)]
        assert my_cards[0] != my_cards[1] # theyre not just references to the same Mock objects
        all_my_cards = cast(list[InterfaceCard], my_cards)
        pile = Pile(all_cards=all_my_cards)
        
        last_card_before = pile.getCard(4)
        pile.removeLastCard()
        last_card_after = pile.getCard(4)
        
        assert last_card_before != last_card_after  # The last card should have changed
        assert last_card_after is not None # card is replaced

    def test_pile_state(self) -> None:
        """Test that the state method returns a valid JSON string"""
        card_mock = Mock(spec=InterfaceCard)
        card_mock.state.return_value = '{"name": "Test Card"}'
        pile_mock = Pile(all_cards=[card_mock]*10)
        
        state_str = pile_mock.state()
        print(state_str)
        import json
        state = json.loads(state_str)
        assert "visible_cards" in state
        assert "hidden_cards_count" in state
        assert len(state["visible_cards"]) == 4
        assert state["hidden_cards_count"] == 6
