import pytest
from unittest.mock import Mock
from terra_futura.game import Game
from terra_futura.player import Player
from terra_futura.simple_types import GameState, Deck, CardSource, GridPosition, Resource
from terra_futura.select_reward import SelectReward
from typing import cast
from terra_futura.interfaces import InterfacePile


class TestGameInitialization:
    """Test game initialization and basic properties"""
    
    def test_game_initialization_valid(self) -> None:
        """Test that game initializes correctly with valid parameters"""
        # Setup
        grid1 = Mock()
        grid2 = Mock()
        player1 = Player(id=1, grid=grid1, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        player2 = Player(id=2, grid=grid2, activation_patterns=[Mock(), Mock()], 
                        scoring_methods=[Mock(), Mock()])
        
        piles_mock = {Deck.LEVEL_I: Mock(), Deck.LEVEL_II: Mock()}
        piles = cast(dict[Deck, InterfacePile], piles_mock)
        move_card = Mock()
        process_action = Mock()
        process_action_assistance = Mock()
        select_reward = Mock()
        game_observer = Mock()
        
        # Execute
        game = Game(
            players=[player1, player2],
            piles=piles,
            moveCard=move_card,
            processAction=process_action,
            processActionAssistance=process_action_assistance,
            selectReward=select_reward,
            gameObserver=game_observer
        )
        
        # Assert
        assert game.state == GameState.TakeCardNoCardDiscarded
        assert game.turnNumber == 1
        assert game.currentPlayerId == 1
        assert len(game.players) == 2
    
    def test_game_initialization_too_many_players(self) -> None:
        """Test that game raises error with too many players"""
        players = cast(list[Player], [Mock(spec=Player) for _ in range(5)])
        piles_mock = {Deck.LEVEL_I: Mock(), Deck.LEVEL_II: Mock()}
        piles = cast(dict[Deck, InterfacePile], piles_mock)
        
        with pytest.raises(ValueError, match="Number of players"):
            Game(
                players=players,
                piles=piles,
                moveCard=Mock(),
                processAction=Mock(),
                processActionAssistance=Mock(),
                selectReward=SelectReward(),
                gameObserver=Mock()
            )
    
    def test_game_initialization_too_few_players(self) -> None:
        """Test that game raises error with too few players"""
        players = cast(list[Player], [Mock(spec=Player)])
        piles_mock = {Deck.LEVEL_I: Mock(), Deck.LEVEL_II: Mock()}
        piles = cast(dict[Deck, InterfacePile], piles_mock)
        
        with pytest.raises(ValueError, match="Number of players"):
            Game(
                players=players,
                piles=piles,
                moveCard=Mock(),
                processAction=Mock(),
                processActionAssistance=Mock(),
                selectReward=SelectReward(),
                gameObserver=Mock()
            )
    
    def test_game_initialization_wrong_pile_count(self) -> None:
        """Test that game raises error with wrong number of piles"""
        players = cast(list[Player], [Mock(spec=Player), Mock(spec=Player)])
        piles_mock = {Deck.LEVEL_I: Mock()}  # Only one deck
        piles = cast(dict[Deck, InterfacePile], piles_mock)

        with pytest.raises(ValueError, match="Wrong number of decks"):
            Game(
                players=players,
                piles=piles,
                moveCard=Mock(),
                processAction=Mock(),
                processActionAssistance=Mock(),
                selectReward=SelectReward(),
                gameObserver=Mock()
            )


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

