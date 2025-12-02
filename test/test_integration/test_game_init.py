import pytest
from unittest.mock import Mock
from terra_futura.game import Game
from terra_futura.player import Player
from terra_futura.simple_types import GameState, Deck
from terra_futura.select_reward import SelectReward
from typing import cast
from terra_futura.interfaces import InterfacePile

class TestGameInitialization:
    """Test game initialization and basic properties"""
    
    def test_game_initialization_valid(self) -> None:
        """Test that game initializes correctly with valid parameters"""
        # Setup
        grid1 = Mock()
        grid2 = Mock()
        player1 = Player(id=1, grid=grid1, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        player2 = Player(id=2, grid=grid2, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        
        piles_mock = {Deck.LEVEL_I: Mock(), Deck.LEVEL_II: Mock()}
        piles = cast(dict[Deck, InterfacePile], piles_mock)
        move_card = Mock()
        process_action = Mock()
        process_action_assistance = Mock()
        select_reward = Mock()
        game_observer = Mock()
        
        # Execute
        game = Game(
            players=[player1, player2],
            piles=piles,
            moveCard=move_card,
            processAction=process_action,
            processActionAssistance=process_action_assistance,
            selectReward=select_reward,
            gameObserver=game_observer
        )
        
        # Assert
        assert game.state == GameState.TakeCardNoCardDiscarded
        assert game.turnNumber == 1
        assert game.currentPlayerId == 1
        assert len(game.players) == 2
    
    def test_game_initialization_too_many_players(self) -> None:
        """Test that game raises error with too many players"""
        players = cast(list[Player], [Mock(spec=Player) for _ in range(5)])
        piles_mock = {Deck.LEVEL_I: Mock(), Deck.LEVEL_II: Mock()}
        piles = cast(dict[Deck, InterfacePile], piles_mock)
        
        with pytest.raises(ValueError, match="Number of players"):
            Game(
                players=players,
                piles=piles,
                moveCard=Mock(),
                processAction=Mock(),
                processActionAssistance=Mock(),
                selectReward=SelectReward(),
                gameObserver=Mock()
            )
    
    def test_game_initialization_too_few_players(self) -> None:
        """Test that game raises error with too few players"""
        players = cast(list[Player], [Mock(spec=Player)])
        piles_mock = {Deck.LEVEL_I: Mock(), Deck.LEVEL_II: Mock()}
        piles = cast(dict[Deck, InterfacePile], piles_mock)
        
        with pytest.raises(ValueError, match="Number of players"):
            Game(
                players=players,
                piles=piles,
                moveCard=Mock(),
                processAction=Mock(),
                processActionAssistance=Mock(),
                selectReward=SelectReward(),
                gameObserver=Mock()
            )
    
    def test_game_initialization_wrong_pile_count(self) -> None:
        """Test that game raises error with wrong number of piles"""
        players = cast(list[Player], [Mock(spec=Player), Mock(spec=Player)])
        piles_mock = {Deck.LEVEL_I: Mock()}  # Only one deck
        piles = cast(dict[Deck, InterfacePile], piles_mock)

        with pytest.raises(ValueError, match="Wrong number of decks"):
            Game(
                players=players,
                piles=piles,
                moveCard=Mock(),
                processAction=Mock(),
                processActionAssistance=Mock(),
                selectReward=SelectReward(),
                gameObserver=Mock()
            )
