from unittest.mock import Mock
from terra_futura.simple_types import GridPosition
from terra_futura.interfaces import InterfaceCard
from terra_futura.player import Player
from typing import cast, Any
from terra_futura.grid import Grid
import json

class TestGrid:
    def test_put_card(self) -> None:
        """Test that putCard is called correctly"""
        # Setup
        card_mock = Mock(spec=InterfaceCard)
        grid_mock = Grid()
        
        player = Player(
            id=0,
            activation_patterns=[Mock(), Mock()],
            scoring_methods=[Mock(), Mock()],
            grid=grid_mock
        )
        assert grid_mock.getCard(GridPosition(0, 0)) is None
        player.getGrid().putCard(GridPosition(0, 0), card_mock) # place a card in the 0, 0 spot
        assert grid_mock.getCard(GridPosition(0, 0)) is not None # card should be there

    def test_grid_state(self) -> None:
        """Test that the grid state is returned correctly"""

        card_mock = Mock(spec=InterfaceCard)
        card_mock.state.return_value = '{"name": "Test Card"}'
        grid_mock = Grid()
        grid_mock.putCard(GridPosition(0, 0), card_mock)
        
        state_str = grid_mock.state()
        state = cast(dict[Any, Any], json.loads(state_str))
        
        assert state is not None
        assert len(state["cards"]) == 1
        assert state["cards"][0]["card"] == '{"name": "Test Card"}'


    def test_can_put_card(self) -> None:
        """Test that canPutCard works correctly"""
        # Setup
        card_mock = Mock(spec=InterfaceCard)
        grid = Grid()
        
        # Action & Assert
        assert grid.canPutCard(GridPosition(0, 0)) is True
        grid.putCard(GridPosition(0, 0), card_mock)
        assert grid.canPutCard(GridPosition(0, 0)) is False