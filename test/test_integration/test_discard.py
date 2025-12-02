from unittest.mock import Mock
from terra_futura.game import Game
from terra_futura.player import Player
from terra_futura.simple_types import GameState, Deck
from terra_futura.select_reward import SelectReward
from typing import cast
from terra_futura.interfaces import InterfacePile

class TestDiscardCard:
    """Test discarding cards from deck"""
    
    def test_discard_card_valid(self) -> None:
        """Test that player can discard card on their turn"""
        # Setup
        grid = Mock()
        player = Player(id=1, grid=grid, activation_patterns=[Mock(), Mock()], 
                       scoring_methods=[Mock(), Mock()])
        pile_mock = Mock()
        piles_mock = {Deck.LEVEL_I: pile_mock, Deck.LEVEL_II: Mock()}
        piles = cast(dict[Deck, InterfacePile], piles_mock)
        observer_mock = Mock()
        
        game = Game(
            players=[player, Mock()],
            piles=piles,
            moveCard=Mock(),
            processAction=Mock(),
            processActionAssistance=Mock(),
            selectReward=SelectReward(),
            gameObserver=observer_mock
        )
        
        # Execute
        result = game.discardLastCardFromDeck(1, Deck.LEVEL_I)
        
        # Assert
        assert result == True
        assert game.state == GameState.TakeCardCardDiscarded
        pile_mock.removeLastCard.assert_called_once()
        observer_mock.notifyAll.assert_called_once()
    
    def test_discard_card_wrong_player(self) -> None:
        """Test that player cannot discard when it's not their turn"""
        # Setup
        player1 = Mock()
        player1.id = 1
        player2 = Mock()
        player2.id = 2
        
        game = Game(
            players=[player1, player2],
            piles={Deck.LEVEL_I: Mock(), Deck.LEVEL_II: Mock()},
            moveCard=Mock(),
            processAction=Mock(),
            processActionAssistance=Mock(),
            selectReward=SelectReward(),
            gameObserver=Mock()
        )
        
        # Execute
        result = game.discardLastCardFromDeck(2, Deck.LEVEL_I)  # Player 2 tries on Player 1's turn
        
        # Assert
        assert result == False
        assert game.state == GameState.TakeCardNoCardDiscarded
    
    def test_discard_card_wrong_state(self) -> None:
        """Test that player cannot discard after already discarding"""
        # Setup
        grid = Mock()
        player1 = Player(id=1, grid=grid, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        player2 = Player(id=2, grid=Mock(), activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        
        game = Game(
            players=[player1, player2],
            piles={Deck.LEVEL_I: Mock(), Deck.LEVEL_II: Mock()},
            moveCard=Mock(),
            processAction=Mock(),
            processActionAssistance=Mock(),
            selectReward=SelectReward(),
            gameObserver=Mock()
        )
        
        game._state = GameState.TakeCardCardDiscarded
        
        # Execute
        result = game.discardLastCardFromDeck(1, Deck.LEVEL_I)
        
        # Assert
        assert result == False
