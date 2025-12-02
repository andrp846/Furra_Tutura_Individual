from unittest.mock import Mock
from terra_futura.game import Game
from terra_futura.player import Player
from terra_futura.simple_types import GameState, Deck
from terra_futura.select_reward import SelectReward

class TestEndgame:
    """Test endgame activation patterns and scoring"""
    
    def test_select_activation_pattern_valid(self) -> None:
        """Test selecting activation pattern"""
        # Setup
        grid_mock = Mock()
        grid_mock.state.return_value = "{}"
        pattern1 = Mock()
        pattern1.select.return_value = None
        pattern2 = Mock()
        
        player1 = Player(id=1, grid=grid_mock, activation_patterns=[pattern1, pattern2], 
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
        
        game._state = GameState.SelectActivationPattern
        
        # Execute
        result = game.selectActivationPattern(1, 0)
        
        # Assert
        assert result == True
        assert game.state == GameState.ActivateCard
        pattern1.select.assert_called_once()
        observer_mock.notifyAll.assert_called_once()
    
    def test_select_activation_pattern_invalid_index(self) -> None:
        """Test selecting invalid activation pattern index"""
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
        
        game._state = GameState.SelectActivationPattern
        
        # Execute
        result = game.selectActivationPattern(1, 2)  # Invalid index
        
        # Assert
        assert result == False
        assert game.state == GameState.SelectActivationPattern
    
    def test_select_scoring_valid(self) -> None:
        """Test selecting scoring method"""
        # Setup
        grid_mock = Mock()
        grid_mock.state.return_value = "{}"
        scoring1 = Mock()
        scoring1.selectThisMethodAndCalculate.return_value = None
        scoring2 = Mock()
        
        player1 = Player(id=1, grid=grid_mock, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[scoring1, scoring2])
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
        
        game._state = GameState.SelectScoringMethod
        game._onTurn = 1  # Player 2's turn (last player)
        
        # Execute
        result = game.selectScoring(2, 0)
        
        # Assert - Should finish when last player selects
        assert result == True
        # After player 2 (index 1) advances, _onTurn becomes 0 (player 1)
        # So game should transition to Finish
        assert game.state == GameState.Finish
        observer_mock.notifyAll.assert_called_once()
    
    def test_select_scoring_multiple_players(self) -> None:
        """Test that scoring stays in SelectScoringMethod until all players done"""
        # Setup
        grid1_mock = Mock()
        grid1_mock.state.return_value = "{}"
        grid2_mock = Mock()
        grid2_mock.state.return_value = "{}"
        
        scoring1 = Mock()
        scoring1.selectThisMethodAndCalculate.return_value = None
        
        player1 = Player(id=1, grid=grid1_mock, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[scoring1, Mock()])
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
        
        game._state = GameState.SelectScoringMethod
        
        # Execute
        result = game.selectScoring(1, 0)
        
        # Assert
        assert result == True
        assert game.state == GameState.SelectScoringMethod  # Still in scoring
        assert game.currentPlayerId == 2  # Next player's turn

