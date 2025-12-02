"""
Full Integration Test for Terra Futura Game

This test simulates a complete 2-player game from start to finish:
- Card placement and activation
- Resource management
- Turn progression
- Endgame (activation patterns and scoring)
"""

from terra_futura.game import Game
from terra_futura.player import Player
from terra_futura.grid import Grid
from terra_futura.card import Card
from terra_futura.pile import Pile
from terra_futura.move_card import MoveCard
from terra_futura.process_action import ProcessAction
from terra_futura.process_action_assistance import ProcessActionAssistance
from terra_futura.select_reward import SelectReward
from terra_futura.game_observer import GameObserver
from terra_futura.activation_pattern import ActivationPattern
from terra_futura.scoring_method import ScoringMethod
from terra_futura.transformation_fixed import TransformationFixed
from terra_futura.arbitrary_basic import ArbitraryBasic
from terra_futura.simple_types import (
    Resource, Deck, CardSource, GridPosition, 
    GameState, Points
)
from terra_futura.interfaces import TerraFuturaObserverInterface, InterfaceCard, InterfacePile


class GameNotificationObserver(TerraFuturaObserverInterface):
    """Simple observer that records notifications"""
    def __init__(self) -> None:
        self.notifications: list[str] = []
    
    def notify(self, game_state: str) -> None:
        self.notifications.append(game_state)


class TestFullGameIntegration:
    """
    Full integration test: Complete 2-player game simulation
    
    Game scenario:
    - 2 players
    - Simplified cards with production and transformation effects
    - 2 turns per player (instead of full 9 for brevity)
    - Endgame with activation patterns and scoring
    """
    
    def create_production_card(self, resource: Resource, pollution_spaces: int = 2) -> Card:
        """Create a card that produces a resource"""
        effect = TransformationFixed(
            from_=[],  # No input
            to=[resource],  # Produces resource
            pollution=0
        )
        return Card(pollutionSpacesL=pollution_spaces, upperEffect=effect)
    
    def create_transformation_card(self, from_res: Resource, to_res: Resource, 
                                   pollution: int = 0, pollution_spaces: int = 2) -> Card:
        """Create a card that transforms one resource into another"""
        effect = TransformationFixed(
            from_=[from_res],
            to=[to_res],
            pollution=pollution
        )
        return Card(pollutionSpacesL=pollution_spaces, upperEffect=effect)
    
    def create_starting_card(self) -> Card:
        """Create a starting card with arbitrary resource production"""
        effect = ArbitraryBasic(
            from_=0,  # No cost
            to=[Resource.YELLOW],  # Produces yellow
            pollution=0
        )
        return Card(pollutionSpacesL=2, upperEffect=effect)
    
    def test_complete_game_flow(self) -> None:
        """
        Integration Test: Complete game from start to finish
        
        Flow:
        1. Setup game with 2 players
        2. Turn 1 - Player 1: Take card, activate, finish turn
        3. Turn 1 - Player 2: Take card, activate, finish turn
        4. Turn 2 - Player 1: Take card, activate (with production chain), finish
        5. Turn 2 - Player 2: Take card, activate, finish
        6. Endgame: Activation patterns
        7. Scoring
        """
        
        # ============================================================
        # SETUP PHASE
        # ============================================================
        
        # Create observers
        observer1 = GameNotificationObserver()
        observer2 = GameNotificationObserver()
        game_observer = GameObserver({1: observer1, 2: observer2})
        
        # Create grids for players
        grid1 = Grid()
        grid2 = Grid()
        
        # Create activation patterns (simplified - just activate center card)
        pattern1_positions = [GridPosition(0, 0)]
        pattern2_positions = [GridPosition(0, 0)]
        activation_pattern1_1 = ActivationPattern(grid1, pattern1_positions)
        activation_pattern1_2 = ActivationPattern(grid1, pattern2_positions)
        activation_pattern2_1 = ActivationPattern(grid2, pattern1_positions)
        activation_pattern2_2 = ActivationPattern(grid2, pattern2_positions)
        
        # Create scoring methods
        scoring1_1 = ScoringMethod([Resource.FOOD], Points(10), grid1)
        scoring1_2 = ScoringMethod([Resource.GREEN], Points(5), grid1)
        scoring2_1 = ScoringMethod([Resource.FOOD], Points(10), grid2)
        scoring2_2 = ScoringMethod([Resource.GREEN], Points(5), grid2)
        
        # Create players with starting cards
        starting_card1 = self.create_starting_card()
        starting_card2 = self.create_starting_card()
        grid1.putCard(GridPosition(0, 0), starting_card1)
        grid2.putCard(GridPosition(0, 0), starting_card2)
        
        player1 = Player(
            id=1,
            grid=grid1,
            activation_patterns=[activation_pattern1_1, activation_pattern1_2],
            scoring_methods=[scoring1_1, scoring1_2]
        )
        
        player2 = Player(
            id=2,
            grid=grid2,
            activation_patterns=[activation_pattern2_1, activation_pattern2_2],
            scoring_methods=[scoring2_1, scoring2_2]
        )
        
        # Create card decks
        # Deck I: Production cards (produce resources from nothing)
        deck_i_cards: list[InterfaceCard] = [
            self.create_production_card(Resource.GREEN),
            self.create_production_card(Resource.RED),
            self.create_production_card(Resource.YELLOW),
            self.create_production_card(Resource.GREEN),
        ]
        
        # Deck II: Transformation cards (convert resources)
        deck_ii_cards: list[InterfaceCard] = [
            self.create_transformation_card(Resource.GREEN, Resource.FOOD, pollution=1),
            self.create_transformation_card(Resource.RED, Resource.CONSTRUCTION, pollution=1),
            self.create_transformation_card(Resource.YELLOW, Resource.GOODS, pollution=0),
            self.create_transformation_card(Resource.GREEN, Resource.FOOD, pollution=0),
        ]
        
        pile_i = Pile(deck_i_cards)
        pile_ii = Pile(deck_ii_cards)
        piles: dict[Deck, InterfacePile] = {Deck.LEVEL_I: pile_i, Deck.LEVEL_II: pile_ii}
        
        # Create game components
        move_card = MoveCard()
        process_action = ProcessAction()
        process_action_assistance = ProcessActionAssistance()
        select_reward = SelectReward()
        
        # Create game (start at turn 8 to simulate near-end of game - only 2 turns)
        game = Game(
            players=[player1, player2],
            piles=piles,
            moveCard=move_card,
            processAction=process_action,
            processActionAssistance=process_action_assistance,
            selectReward=select_reward,
            gameObserver=game_observer
        )
        
        # Manually set turn number to 8 (so next turns are 8 and 9)
        game._turnNumber = 8
        
        # ============================================================
        # TURN 8 - PLAYER 1
        # ============================================================
        
        assert game.state == GameState.TakeCardNoCardDiscarded
        assert game.currentPlayerId == 1
        assert game.turnNumber == 8
        
        # Player 1 takes a production card from Deck I
        source = CardSource(deck=Deck.LEVEL_I, index=1)
        result = game.takeCard(1, source, 1, GridPosition(1, 0))
        assert result == True
        assert game.state == GameState.ActivateCard # type: ignore[comparison-overlap]
        
        # Activate the newly placed card (produces GREEN)
        # The card at (1,0) will activate, plus starting card at (0,0)
        game.activateCard(
            playerId=1,
            card=GridPosition(1, 0),
            inputs=[],  # Production card needs no input
            outputs=[(Resource.GREEN, GridPosition(1, 0))],  # Output goes on the card
            pollution=[],
            otherPlayerId=None,
            otherCard=None
        )
        
        # Verify resource was produced
        card_1_0 = grid1.getCard(GridPosition(1, 0))
        assert Resource.GREEN in card_1_0.resources
        assert game.state == GameState.ActivateCard
        
        # Player 1 finishes turn
        result = game.turnFinished(1)
        assert result == True
        assert game.state == GameState.TakeCardNoCardDiscarded
        assert game.currentPlayerId == 2  # Player 2's turn
        
        # ============================================================
        # TURN 8 - PLAYER 2
        # ============================================================
        
        # Player 2 takes a production card
        source = CardSource(deck=Deck.LEVEL_I, index=2)
        result = game.takeCard(2, source, 2, GridPosition(-1, 0))
        assert result == True
        
        # Activate card
        game.activateCard(
            playerId=2,
            card=GridPosition(-1, 0),
            inputs=[],
            outputs=[(Resource.RED, GridPosition(-1, 0))],
            pollution=[],
            otherPlayerId=None,
            otherCard=None
        )
        
        # Finish turn
        result = game.turnFinished(2)
        assert result == True
        assert game.currentPlayerId == 1
        assert game.turnNumber == 9  # Now turn 9 (last regular turn)
        
        # ============================================================
        # TURN 9 - PLAYER 1 (Last regular turn)
        # ============================================================
        
        # Player 1 takes a transformation card (GREEN -> FOOD with pollution)
        source = CardSource(deck=Deck.LEVEL_II, index=1)
        result = game.takeCard(1, source, 1, GridPosition(0, 1))
        assert result == True
        
        # Activate transformation: Use GREEN from (1,0) to produce FOOD at (0,1)
        # This will also produce 1 pollution
        game.activateCard(
            playerId=1,
            card=GridPosition(0, 1),
            inputs=[(Resource.GREEN, GridPosition(1, 0))],  # Take GREEN from previous card
            outputs=[(Resource.FOOD, GridPosition(0, 1))],  # Produce FOOD
            pollution=[GridPosition(0, 1)],  # Place pollution on same card
            otherPlayerId=None,
            otherCard=None
        )
        
        # Verify transformation happened
        card_1_0 = grid1.getCard(GridPosition(1, 0))
        card_0_1 = grid1.getCard(GridPosition(0, 1))
        assert Resource.GREEN not in card_1_0.resources  # GREEN was consumed
        assert Resource.FOOD in card_0_1.resources  # FOOD was produced
        assert card_0_1.pollution == 1  # Pollution was placed
        
        # Finish turn
        result = game.turnFinished(1)
        assert result == True
        assert game.currentPlayerId == 2
        
        # ============================================================
        # TURN 9 - PLAYER 2 (Last regular turn)
        # ============================================================
        
        # Player 2 takes a transformation card
        source = CardSource(deck=Deck.LEVEL_II, index=2)
        result = game.takeCard(2, source, 2, GridPosition(0, -1))
        assert result == True
        
        # Activate
        game.activateCard(
            playerId=2,
            card=GridPosition(0, -1),
            inputs=[(Resource.RED, GridPosition(-1, 0))],
            outputs=[(Resource.CONSTRUCTION, GridPosition(0, -1))],
            pollution=[GridPosition(0, -1)],
            otherPlayerId=None,
            otherCard=None
        )
        
        # Finish turn - this should trigger endgame
        result = game.turnFinished(2)
        assert result == True
        assert game.state == GameState.SelectActivationPattern
        assert game.currentPlayerId == 1  # Back to player 1 for endgame
        
        # ============================================================
        # ENDGAME - ACTIVATION PATTERNS
        # ============================================================
        
        # Player 1 selects activation pattern
        result = game.selectActivationPattern(1, 0)  # Select first pattern
        assert result == True
        assert game.state == GameState.ActivateCard
        
        # Player 1 can now activate according to pattern (we'll skip detailed activation)
        # Finish endgame activation
        result = game.turnFinished(1)
        assert result == True
        assert game.state == GameState.SelectActivationPattern
        assert game.currentPlayerId == 2
        
        # Player 2 selects activation pattern
        result = game.selectActivationPattern(2, 1)  # Select second pattern
        assert result == True
        
        # Player 2 finishes endgame activation
        result = game.turnFinished(2)
        assert result == True
        assert game.state == GameState.SelectScoringMethod
        
        # ============================================================
        # SCORING
        # ============================================================
        
        # Player 1 selects scoring method
        result = game.selectScoring(1, 0)  # Select first scoring method (FOOD)
        assert result == True
        assert game.state == GameState.SelectScoringMethod
        assert player1.scoring_methods[0].calculatedTotal is not None
        
        # Player 2 selects scoring method (last player - should finish game)
        result = game.selectScoring(2, 0)
        assert result == True
        assert game.state == GameState.Finish
        
        # Verify both players have calculated scores
        assert player1.scoring_methods[0].calculatedTotal is not None
        assert player2.scoring_methods[0].calculatedTotal is not None
        
        # Verify observers received notifications
        assert len(observer1.notifications) > 0
        assert len(observer2.notifications) > 0
        
    def test_grid_boundaries_and_card_placement(self) -> None:
        """
        Integration Test 3: Grid boundaries and 3x3 constraint
        
        Tests:
        - Valid card placements within 3x3 grid
        - Invalid placements outside grid
        - Grid coordinate system
        """
        
        grid = Grid()
        move_card = MoveCard()
        
        # Create cards
        cards = [self.create_production_card(Resource.GREEN) for _ in range(10)]
        pile = Pile(cards) # type: ignore
        
        # Test valid placements in 3x3 grid (relative coordinates -1 to 1 from center)
        valid_positions = [
            GridPosition(-1, -1), GridPosition(0, -1), GridPosition(1, -1),
            GridPosition(-1, 0),  GridPosition(0, 0),  GridPosition(1, 0),
            GridPosition(-1, 1),  GridPosition(0, 1),  GridPosition(1, 1),
        ]
        
        # Place starting card
        starting_card = cards[0]
        grid.putCard(GridPosition(0, 0), starting_card)
        
        # Test placing cards at valid positions
        for i, pos in enumerate(valid_positions[1:4], start=1):  # Test a few positions
            result = move_card.moveCard(pile, i+1, pos, grid)
            assert result == True, f"Failed to place card at {pos}"
            assert grid.getCard(pos) is not None
        
        # Test invalid placements (outside 3x3 or already occupied)
        # Already occupied position
        result = move_card.moveCard(pile, 5, GridPosition(0, 0), grid)
        assert result == False  # Position already has a card
        