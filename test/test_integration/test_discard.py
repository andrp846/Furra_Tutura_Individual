from unittest.mock import Mock
from terra_futura.game import Game
from terra_futura.player import Player
from terra_futura.simple_types import GameState, Deck
from terra_futura.select_reward import SelectReward
from typing import cast
from terra_futura.interfaces import InterfacePile
from terra_futura.pile import Pile

class TestDiscardCard:
    """Test discarding cards from deck"""
    
    def test_discard_card_valid(self) -> None:
        """Test that player can discard card on their turn"""
        grid = Mock()
        player = Player(id=1, grid=grid, activation_patterns=[Mock(), Mock()], 
                       scoring_methods=[Mock(), Mock()])
        pile_mock = Pile(all_cards=[Mock() for _ in range(10)])
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
        
        card_before = pile_mock.getCard(4)
        result = game.discardLastCardFromDeck(1, Deck.LEVEL_I)
        assert result == True
        card_after = pile_mock.getCard(4)
        assert card_before != card_after
        
        assert game.state == GameState.TakeCardCardDiscarded
    
    def test_discard_card_wrong_player(self) -> None:
        """Test that player cannot discard when it's not their turn"""
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
        
        result = game.discardLastCardFromDeck(2, Deck.LEVEL_I)  # Player 2 tries on Player 1s turn
        
        assert result == False
        assert game.state == GameState.TakeCardNoCardDiscarded # state remains unchanged
    
    def test_discard_card_wrong_state(self) -> None:
        """Test that player cannot discard after already discarding"""
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
        result = game.discardLastCardFromDeck(1, Deck.LEVEL_I)  # First discard
        assert result == True        
        assert game.state == GameState.TakeCardCardDiscarded

        result_2 = game.discardLastCardFromDeck(1, Deck.LEVEL_I) # Second discard
        assert result_2 == False
        # Assert
