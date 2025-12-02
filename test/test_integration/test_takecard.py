from unittest.mock import Mock
from terra_futura.game import Game
from terra_futura.player import Player
from terra_futura.simple_types import GameState, Deck, CardSource, GridPosition
from terra_futura.select_reward import SelectReward


class TestTakeCard:
    """Test taking cards from pile"""
    
    def test_take_card_valid_no_discard(self) -> None:
        """Test taking card without prior discard"""
        # Setup
        grid_mock = Mock()
        grid_mock.state.return_value = "{}"
        player1 = Player(id=1, grid=grid_mock, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        player2 = Player(id=2, grid=Mock(), activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        
        pile_mock = Mock()
        move_card_mock = Mock()
        move_card_mock.moveCard.return_value = True
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
        
        # Execute
        source = CardSource(deck=Deck.LEVEL_I, index=1)
        destination = GridPosition(0, 0)
        result = game.takeCard(1, source, 1, destination)
        
        # Assert
        assert result == True
        assert game.state == GameState.ActivateCard
        move_card_mock.moveCard.assert_called_once_with(pile_mock, 1, destination, grid_mock)
        observer_mock.notifyAll.assert_called_once()
    
    def test_take_card_after_discard(self) -> None:
        """Test taking card after discarding"""
        # Setup
        grid_mock = Mock()
        grid_mock.state.return_value = "{}"
        player1 = Player(id=1, grid=grid_mock, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        player2 = Player(id=2, grid=Mock(), activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        
        move_card_mock = Mock()
        move_card_mock.moveCard.return_value = True
        
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
        
        # Execute
        source = CardSource(deck=Deck.LEVEL_I, index=1)
        destination = GridPosition(0, 0)
        result = game.takeCard(1, source, 1, destination)
        
        # Assert
        assert result == True
        assert game.state == GameState.ActivateCard
    
    def test_take_card_move_fails(self) -> None:
        """Test that takeCard fails if moveCard fails"""
        # Setup
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
        
        # Execute
        source = CardSource(deck=Deck.LEVEL_I, index=1)
        destination = GridPosition(0, 0)
        result = game.takeCard(1, source, 1, destination)
        
        # Assert
        assert result == False
        assert game.state == GameState.TakeCardNoCardDiscarded

