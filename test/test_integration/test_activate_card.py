from unittest.mock import Mock
from terra_futura.game import Game
from terra_futura.player import Player
from terra_futura.simple_types import GameState, Deck, GridPosition, Resource
from terra_futura.select_reward import SelectReward

class TestActivateCard:
    """Test card activation"""
    
    def test_activate_card_normal(self) -> None:
        """Test normal card activation without assistance"""
        # Setup
        grid_mock = Mock()
        grid_mock.state.return_value = "{}"
        card_mock = Mock()
        grid_mock.getCard.return_value = card_mock
        
        player1 = Player(id=1, grid=grid_mock, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        player2 = Player(id=2, grid=Mock(), activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        
        process_action_mock = Mock()
        process_action_mock.activateCard.return_value = True
        observer_mock = Mock()
        
        game = Game(
            players=[player1, player2],
            piles={Deck.LEVEL_I: Mock(), Deck.LEVEL_II: Mock()},
            moveCard=Mock(),
            processAction=process_action_mock,
            processActionAssistance=Mock(),
            selectReward=SelectReward(),
            gameObserver=observer_mock
        )
        
        game._state = GameState.ActivateCard
        
        # Execute
        card_pos = GridPosition(0, 0)
        inputs = [(Resource.GREEN, GridPosition(0, 0))]
        outputs = [(Resource.FOOD, GridPosition(0, 0))]
        pollution: list[GridPosition] = []
        
        game.activateCard(1, card_pos, inputs, outputs, pollution, None, None)
        
        # Assert
        process_action_mock.activateCard.assert_called_once_with(
            card_mock, grid_mock, inputs, outputs, pollution
        )
        observer_mock.notifyAll.assert_called_once()
    
    def test_activate_card_with_assistance(self) -> None:
        """Test card activation with assistance"""
        # Setup
        grid1_mock = Mock()
        grid1_mock.state.return_value = "{}"
        grid2_mock = Mock()
        grid2_mock.state.return_value = "{}"
        
        card1_mock = Mock()
        card2_mock = Mock()
        grid1_mock.getCard.return_value = card1_mock
        grid2_mock.getCard.return_value = card2_mock
        
        player1 = Player(id=1, grid=grid1_mock, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        player2 = Player(id=2, grid=grid2_mock, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        
        process_action_assistance_mock = Mock()
        process_action_assistance_mock.activateCard.return_value = True
        observer_mock = Mock()
        
        game = Game(
            players=[player1, player2],
            piles={Deck.LEVEL_I: Mock(), Deck.LEVEL_II: Mock()},
            moveCard=Mock(),
            processAction=Mock(),
            processActionAssistance=process_action_assistance_mock,
            selectReward=SelectReward(),
            gameObserver=observer_mock
        )
        
        game._state = GameState.ActivateCard
        
        # Execute
        card_pos = GridPosition(0, 0)
        other_card_pos = GridPosition(0, 0)
        inputs = [(Resource.GREEN, GridPosition(0, 0))]
        outputs = [(Resource.FOOD, GridPosition(0, 0))]
        pollution: list[GridPosition] = []
        
        game.activateCard(1, card_pos, inputs, outputs, pollution, 2, other_card_pos)
        
        # Assert
        assert game.state == GameState.SelectReward
        process_action_assistance_mock.activateCard.assert_called_once_with(
            card1_mock, grid1_mock, player2, card2_mock, inputs, outputs, pollution
        )
        observer_mock.notifyAll.assert_called_once()
    
    def test_activate_card_wrong_state(self) -> None:
        """Test that activation fails in wrong state"""
        # Setup
        grid_mock = Mock()
        player = Player(id=1, grid=grid_mock, activation_patterns=[Mock(), Mock()], 
                       scoring_methods=[Mock(), Mock()])
        
        game = Game(
            players=[player, player],
            piles={Deck.LEVEL_I: Mock(), Deck.LEVEL_II: Mock()},
            moveCard=Mock(),
            processAction=Mock(),
            processActionAssistance=Mock(),
            selectReward=SelectReward(),
            gameObserver=Mock()
        )
        
        game._state = GameState.TakeCardNoCardDiscarded  # Wrong state
        
        # Execute
        card_pos = GridPosition(0, 0)
        game.activateCard(1, card_pos, [], [], [], None, None)
        
        # Assert - should do nothing (method returns None)
        assert game.state == GameState.TakeCardNoCardDiscarded
