from unittest.mock import Mock
from terra_futura.game import Game
from terra_futura.player import Player
from terra_futura.simple_types import GameState, Deck
from terra_futura.select_reward import SelectReward

class TestTurnManagement:
    """Test turn progression and management"""
    
    def test_turn_finished_regular_turn(self) -> None:
        """Test finishing a turn during regular play (turns 1-8)"""
        # Setup
        grid_mock = Mock()
        grid_mock.state.return_value = "{}"
        grid_mock.endTurn.return_value = None
        
        player1 = Player(id=1, grid=grid_mock, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        player2 = Player(id=2, grid=Mock(), activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        
        observer_mock = Mock()
        
        game = Game(
            players=[player1, player2],
            piles={Deck.LEVEL_I: Mock(), Deck.LEVEL_II: Mock()},
            moveCard=Mock(),
            processAction=Mock(),
            processActionAssistance=Mock(),
            selectReward=SelectReward(),
            gameObserver=observer_mock
        )
        
        game._state = GameState.ActivateCard
        game._turnNumber = 5
        
        # Execute
        result = game.turnFinished(1)
        
        # Assert
        assert result == True
        assert game.state == GameState.TakeCardNoCardDiscarded
        assert game.currentPlayerId == 2  # Turn passed to player 2
        grid_mock.endTurn.assert_called_once()
        observer_mock.notifyAll.assert_called_once()
    
    def test_turn_finished_turn_9_not_last_player(self) -> None:
        """Test finishing turn 9 when not the last player"""
        # Setup
        grid_mock = Mock()
        grid_mock.state.return_value = "{}"
        grid_mock.endTurn.return_value = None
        
        player1 = Player(id=1, grid=grid_mock, activation_patterns=[Mock(), Mock()], 
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
        
        game._state = GameState.ActivateCard
        game._turnNumber = 9
        
        # Execute
        result = game.turnFinished(1)
        
        # Assert
        assert result == True
        assert game.state == GameState.TakeCardNoCardDiscarded
        assert game.currentPlayerId == 2
    
    def test_turn_finished_turn_9_last_player(self) -> None:
        """Test finishing turn 9 as the last player -> endgame"""
        # Setup
        grid1_mock = Mock()
        grid1_mock.state.return_value = "{}"
        grid1_mock.endTurn.return_value = None
        
        grid2_mock = Mock()
        grid2_mock.state.return_value = "{}"
        grid2_mock.endTurn.return_value = None
        
        player1 = Player(id=1, grid=grid1_mock, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        player2 = Player(id=2, grid=grid2_mock, activation_patterns=[Mock(), Mock()], 
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
        
        game._state = GameState.ActivateCard
        game._turnNumber = 9
        game._onTurn = 1  # Player 2's turn (last player)
        
        # Execute
        result = game.turnFinished(2)
        
        # Assert
        assert result == True
        assert game.state == GameState.SelectActivationPattern
        assert game.currentPlayerId == 1  # Back to first player
    
    def test_turn_finished_wrong_player(self) -> None:
        """Test that player cannot finish turn when it's not their turn"""
        # Setup
        player1 = Player(id=1, grid=Mock(), activation_patterns=[Mock(), Mock()], 
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
        
        game._state = GameState.ActivateCard
        
        # Execute
        result = game.turnFinished(2)  # Player 2 tries on Player 1's turn
        
        # Assert
        assert result == False
        assert game.currentPlayerId == 1
