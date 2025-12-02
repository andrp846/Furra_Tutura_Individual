from unittest.mock import Mock
from terra_futura.game import Game
from terra_futura.player import Player
from terra_futura.simple_types import GameState, Deck, GridPosition, Resource, CardSource
from terra_futura.select_reward import SelectReward
from terra_futura.pile import Pile

class TestActivateCard:
    """Test card activation"""
    
    def test_activate_card_normal(self) -> None:
        """Test normal card activation without assistance"""
        grid_mock = Mock()
        card_mock = Mock()
        grid_mock.getCard.return_value = card_mock
        
        player1 = Player(id=1, grid=grid_mock, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        player2 = Player(id=2, grid=Mock(), activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        
        process_action_mock = Mock()
        process_action_mock.activateCard.return_value = True
        observer_mock = Mock()
        pile = Pile(all_cards=[Mock() for _ in range(10)])
        
        game = Game(
            players=[player1, player2],
            piles={Deck.LEVEL_I: pile, Deck.LEVEL_II: Mock()},
            moveCard=Mock(),
            processAction=process_action_mock,
            processActionAssistance=Mock(),
            selectReward=SelectReward(),
            gameObserver=observer_mock
        )
        
        assert game._state == GameState.TakeCardNoCardDiscarded
        game.takeCard(1, CardSource(Deck.LEVEL_I, 1), 1, GridPosition(0,0))  # Move to ActivateCard state
        assert game._state == GameState.ActivateCard # type: ignore[comparison-overlap]
        assert game.currentPlayerId == 1
    
    def test_activate_card_with_assistance(self) -> None:
        """Test card activation with assistance"""
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
        
        card_pos = GridPosition(0, 0)
        other_card_pos = GridPosition(0, 0)
        inputs = [(Resource.GREEN, GridPosition(0, 0))]
        outputs = [(Resource.FOOD, GridPosition(0, 0))]
        pollution: list[GridPosition] = []
        
        game.activateCard(1, card_pos, inputs, outputs, pollution, 2, other_card_pos)
        
        # we used a card with assistance, now the other player must select a reward
        assert game.state == GameState.SelectReward 
    
    def test_activate_card_wrong_state(self) -> None:
        """Test that activation fails in wrong state"""
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
        
        card_pos = GridPosition(0, 0)
        game.activateCard(1, card_pos, [], [], [], None, None)
        
        assert game.state == GameState.TakeCardNoCardDiscarded
