from unittest.mock import Mock
from terra_futura.game import Game
from terra_futura.player import Player
from terra_futura.simple_types import GameState, Deck, CardSource, GridPosition
from terra_futura.select_reward import SelectReward


class TestTakeCard:
    """Test taking cards from pile"""
    
    def test_take_card_valid_no_discard(self) -> None:
        """Test taking card without prior discard"""
        grid_mock = Mock()
        player1 = Player(id=1, grid=grid_mock, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        player2 = Player(id=2, grid=Mock(), activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        
        pile_mock = Mock()
        move_card_mock = Mock()
        observer_mock = Mock()
        
        game = Game(
            players=[player1, player2],
            piles={Deck.LEVEL_I: pile_mock, Deck.LEVEL_II: Mock()},
            moveCard=move_card_mock,
            processAction=Mock(),
            processActionAssistance=Mock(),
            selectReward=SelectReward(),
            gameObserver=observer_mock
        )
        
        source = CardSource(deck=Deck.LEVEL_I, index=1)
        destination = GridPosition(0, 0)
        result = game.takeCard(1, source, 1, destination)
        
        assert result == True
        assert game.state == GameState.ActivateCard
    
    def test_take_card_after_discard(self) -> None:
        """Test taking card after discarding"""
        grid_mock = Mock()
        player1 = Player(id=1, grid=grid_mock, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        player2 = Player(id=2, grid=Mock(), activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        
        move_card_mock = Mock()
        
        game = Game(
            players=[player1, player2],
            piles={Deck.LEVEL_I: Mock(), Deck.LEVEL_II: Mock()},
            moveCard=move_card_mock,
            processAction=Mock(),
            processActionAssistance=Mock(),
            selectReward=SelectReward(),
            gameObserver=Mock()
        )
        
        game._state = GameState.TakeCardCardDiscarded
        source = CardSource(deck=Deck.LEVEL_I, index=1)
        destination = GridPosition(0, 0)
        result = game.takeCard(1, source, 1, destination)
        
        assert result == True
        assert game.state == GameState.ActivateCard
    
    def test_take_card_move_fails(self) -> None:
        """Test that takeCard fails if moveCard fails"""
        grid_mock = Mock()
        player1 = Player(id=1, grid=grid_mock, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        player2 = Player(id=2, grid=Mock(), activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        
        move_card_mock = Mock()
        move_card_mock.moveCard.return_value = False  # Move fails
        
        game = Game(
            players=[player1, player2],
            piles={Deck.LEVEL_I: Mock(), Deck.LEVEL_II: Mock()},
            moveCard=move_card_mock,
            processAction=Mock(),
            processActionAssistance=Mock(),
            selectReward=SelectReward(),
            gameObserver=Mock()
        )
        
        source = CardSource(deck=Deck.LEVEL_I, index=1)
        destination = GridPosition(0, 0)
        result = game.takeCard(1, source, 1, destination)
        assert result == False
        assert game.state == GameState.TakeCardNoCardDiscarded

