from unittest.mock import Mock
from terra_futura.game import Game
from terra_futura.player import Player
from terra_futura.simple_types import GameState, Deck, Resource
from terra_futura.select_reward import SelectReward

class TestSelectReward:
    """Test reward selection after assistance"""
    
    def test_select_reward_valid(self) -> None:
        """Test valid reward selection"""
        # Setup
        grid_mock = Mock()
        grid_mock.state.return_value = "{}"
        card_mock = Mock()
        card_mock.canPutResources.return_value = True
        card_mock.putResources.return_value = None
        
        player1 = Player(id=2, grid=grid_mock, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        player2 = Player(id=1, grid=Mock(), activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        
        select_reward = SelectReward()
        select_reward.setReward(2, card_mock, [Resource.GREEN, Resource.RED])
        observer_mock = Mock()
        
        game = Game(
            players=[player1, player2],
            piles={Deck.LEVEL_I: Mock(), Deck.LEVEL_II: Mock()},
            moveCard=Mock(),
            processAction=Mock(),
            processActionAssistance=Mock(),
            selectReward=select_reward,
            gameObserver=observer_mock
        )
        
        game._state = GameState.SelectReward
        
        # Execute
        game.selectReward(2, Resource.GREEN)
        
        # Assert
        assert game.state == GameState.ActivateCard
        card_mock.putResources.assert_called_once_with([Resource.GREEN])
        observer_mock.notifyAll.assert_called_once()
    
    def test_select_reward_wrong_player(self) -> None:
        """Test that wrong player cannot select reward"""
        # Setup
        grid_mock = Mock()
        card_mock = Mock()
        
        player1 = Player(id=1, grid=grid_mock, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        player2 = Player(id=2, grid=Mock(), activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        
        select_reward = SelectReward()
        select_reward.setReward(2, card_mock, [Resource.GREEN])  # Reward belongs to player 2
        
        game = Game(
            players=[player1, player2],
            piles={Deck.LEVEL_I: Mock(), Deck.LEVEL_II: Mock()},
            moveCard=Mock(),
            processAction=Mock(),
            processActionAssistance=Mock(),
            selectReward=select_reward,
            gameObserver=Mock()
        )
        
        game._state = GameState.SelectReward
        
        # Execute
        game.selectReward(1, Resource.GREEN)  # Player 1 tries to select
        
        # Assert - should do nothing
        assert game.state == GameState.SelectReward
    
    def test_select_reward_invalid_resource(self) -> None:
        """Test that selecting unavailable resource fails"""
        # Setup
        grid_mock = Mock()
        card_mock = Mock()
        
        player1 = Player(id=2, grid=grid_mock, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        player2 = Player(id=1, grid=Mock(), activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        
        select_reward = SelectReward()
        select_reward.setReward(2, card_mock, [Resource.GREEN])  # Only GREEN available
        
        game = Game(
            players=[player1, player2],
            piles={Deck.LEVEL_I: Mock(), Deck.LEVEL_II: Mock()},
            moveCard=Mock(),
            processAction=Mock(),
            processActionAssistance=Mock(),
            selectReward=select_reward,
            gameObserver=Mock()
        )
        
        game._state = GameState.SelectReward
        
        # Execute
        game.selectReward(2, Resource.RED)  # Try to select RED (not available)
        
        # Assert - should do nothing
        assert game.state == GameState.SelectReward

