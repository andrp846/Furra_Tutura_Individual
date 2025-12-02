from unittest.mock import Mock
from terra_futura.game import Game
from terra_futura.simple_types import Deck, GridPosition
from terra_futura.select_reward import SelectReward
from terra_futura.interfaces import InterfaceCard, InterfaceGrid
from terra_futura.pile import Pile
from terra_futura.player import Player
from typing import cast, Any
from terra_futura.grid import Grid
import json

class TestGrid:
    def test_put_card_called(self) -> None:
        """Test that putCard is called correctly"""
        # Setup
        card_mock = Mock(spec=InterfaceCard)
        grid_mock = Mock(spec=InterfaceGrid)
        
        player = Player(
            id=0,
            activation_patterns=[Mock(), Mock()],
            scoring_methods=[Mock(), Mock()],
            grid=grid_mock
        )
        player.getGrid().putCard(GridPosition(0, 0), card_mock)
        
        grid_mock.putCard.assert_called_once_with(GridPosition(0, 0), card_mock)
        assert grid_mock.getCard(GridPosition(0, 0)) is not None


    def test_grid_state(self) -> None:
        """Test that the grid state is returned correctly"""
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
        
        # Action
        state_str = pile_mock.state()
        state = cast(dict[Any, Any], json.loads(state_str))
        
        # Assert
        assert state is not None

    def test_can_put_card(self) -> None:
        """Test that canPutCard works correctly"""
        # Setup
        card_mock = Mock(spec=InterfaceCard)
        grid = Grid()
        
        # Action & Assert
        assert grid.canPutCard(GridPosition(0, 0)) is True
        grid.putCard(GridPosition(0, 0), card_mock)
        assert grid.canPutCard(GridPosition(0, 0)) is False