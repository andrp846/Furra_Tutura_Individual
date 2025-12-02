from unittest.mock import Mock
from terra_futura.game import Game
from terra_futura.player import Player
from terra_futura.simple_types import GameState, Deck, CardSource, GridPosition
from terra_futura.select_reward import SelectReward

class TestGameIntegration:
    """Integration tests for full game flow"""
    
    def test_full_turn_cycle(self) -> None:
        """Test a complete turn cycle: discard -> take -> activate -> finish"""
        # Setup
        grid_mock = Mock()
        grid_mock.state.return_value = "{}"
        grid_mock.getCard.return_value = Mock()
        grid_mock.endTurn.return_value = None
        
        player1 = Player(id=1, grid=grid_mock, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        player2 = Player(id=2, grid=Mock(), activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        
        pile_mock = Mock()
        pile_mock.removeLastCard.return_value = None
        
        move_card_mock = Mock()
        move_card_mock.moveCard.return_value = True
        
        process_action_mock = Mock()
        process_action_mock.activateCard.return_value = True
        
        game = Game(
            players=[player1, player2],
            piles={Deck.LEVEL_I: pile_mock, Deck.LEVEL_II: Mock()},
            moveCard=move_card_mock,
            processAction=process_action_mock,
            processActionAssistance=Mock(),
            selectReward=SelectReward(),
            gameObserver=Mock()
        )
        
        # Execute full cycle
        # 1. Discard
        assert game.discardLastCardFromDeck(1, Deck.LEVEL_I) == True
        assert game.state == GameState.TakeCardCardDiscarded 
        
        # 2. Take card
        source = CardSource(deck=Deck.LEVEL_I, index=1)
        assert game.takeCard(1, source, 1, GridPosition(0, 0)) == True
        assert game.state == GameState.ActivateCard # type: ignore[comparison-overlap]
        
        # 3. Activate card
        game.activateCard(1, GridPosition(0, 0), [], [], [], None, None)
        assert game.state == GameState.ActivateCard
        
        # 4. Finish turn
        assert game.turnFinished(1) == True
        assert game.state == GameState.TakeCardNoCardDiscarded
        assert game.turnNumber == 1  # Still turn 1
        assert game.currentPlayerId == 2  # Now player 2's turn

