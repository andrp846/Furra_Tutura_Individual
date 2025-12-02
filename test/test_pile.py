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
        # Setup
        pile_mock = Mock()
        
        game = Game(
            players=[Mock(), Mock()],
            piles={Deck.LEVEL_I: pile_mock, Deck.LEVEL_II: Mock()},
            moveCard=Mock(),
            processAction=Mock(),
            processActionAssistance=Mock(),
            selectReward=SelectReward(),
            gameObserver=Mock()
        )
        
        # Assert
        assert game._piles[Deck.LEVEL_I] == pile_mock

    def test_move_card_called(self) -> None:
        """Test that moveCard is called correctly"""
        # Setup
        move_card_mock = Mock()
        pile_mock = Mock()
        grid_mock = Mock()
        
        game = Game(
            players=[Mock(), Mock()],
            piles={Deck.LEVEL_I: pile_mock, Deck.LEVEL_II: Mock()},
            moveCard=move_card_mock,
            processAction=Mock(),
            processActionAssistance=Mock(),
            selectReward=SelectReward(),
            gameObserver=Mock()
        )
        
        # Action
        game._moveCard.moveCard(pile_mock, 0, GridPosition(0, 0), grid_mock)
        
        # Assert
        move_card_mock.moveCard.assert_called_once_with(pile_mock, 0, GridPosition(0, 0), grid_mock)

    def test_take_card(self) -> None:
        """Test that takeCard is called correctly"""
        # Setup
        card_mock = Mock(spec=InterfaceCard)
        pile_mock = Pile(all_cards=[card_mock]*10)
        
        game = Game(
            players=[Mock(), Mock()],
            piles={Deck.LEVEL_I: pile_mock, Deck.LEVEL_II: Mock()},
            moveCard=Mock(),
            processAction=Mock(),
            processActionAssistance=Mock(),
            selectReward=SelectReward(),
            gameObserver=Mock()
        )
        
        # Action
        assert pile_mock.getCard(1) == card_mock
        pile_mock.takeCard(1)
        assert pile_mock.getCard(1) == card_mock  # The next card should now be at index 1

    def test_remove_last_card(self) -> None:
        """Test that removeLastCard works correctly"""
        # Setup
        card_mock = Mock(spec=InterfaceCard)
        my_cards = [Mock(spec=InterfaceCard) for _ in range(10)]
        assert my_cards[0] != my_cards[1] # theyre not just references to the same Mock objects
        all_my_cards = cast(list[InterfaceCard], my_cards)
        pile_mock = Pile(all_cards=all_my_cards)
        
        game = Game(
            players=[Mock(), Mock()],
            piles={Deck.LEVEL_I: pile_mock, Deck.LEVEL_II: Mock()},
            moveCard=Mock(),
            processAction=Mock(),
            processActionAssistance=Mock(),
            selectReward=SelectReward(),
            gameObserver=Mock()
        )
        
        # Action
        last_card_before = pile_mock.getCard(4)
        pile_mock.removeLastCard()
        last_card_after = pile_mock.getCard(4)
        
        # Assert
        assert last_card_before != last_card_after  # The last card should have changed
        assert last_card_after is not None # card is replaced

    def test_pile_state(self) -> None:
        """Test that the state method returns a valid JSON string"""
        # Setup
        card_mock = Mock(spec=InterfaceCard)
        card_mock.state.return_value = '{"name": "Test Card"}'
        pile_mock = Pile(all_cards=[card_mock]*10)
        
        game = Game(
            players=[Mock(), Mock()],
            piles={Deck.LEVEL_I: pile_mock, Deck.LEVEL_II: Mock()},
            moveCard=Mock(),
            processAction=Mock(),
            processActionAssistance=Mock(),
            selectReward=SelectReward(),
            gameObserver=Mock()
        )
        
        state_str = pile_mock.state()
        print(state_str)
        import json
        state = json.loads(state_str)
        assert "visible_cards" in state
        assert "hidden_cards_count" in state
        assert len(state["visible_cards"]) == 4
        assert state["hidden_cards_count"] == 6
