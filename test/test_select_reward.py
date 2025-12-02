import pytest
from unittest.mock import Mock
from terra_futura.simple_types import Resource
from terra_futura.select_reward import SelectReward
from terra_futura.interfaces import InterfaceCard
from terra_futura.select_reward import SelectReward
import json


class TestSelectReward:
    def test_select_reward(self) -> None:
        card_mock = Mock(spec=InterfaceCard)
        card_mock.canPutResources.return_value = True
        
        select_reward = SelectReward()
        select_reward.setReward(player=1, card=card_mock, reward=[Resource.RED, Resource.CONSTRUCTION])
        
        # Action
        assert select_reward.canSelectReward(Resource.RED) is True
        select_reward.selectReward(Resource.RED)
        
        # Assert
        card_mock.putResources.assert_called_once_with([Resource.RED])
        assert select_reward.canSelectReward(Resource.RED) is False

    def test_cannot_select_invalid_reward(self) -> None:
        card_mock = Mock(spec=InterfaceCard)
        card_mock.canPutResources.return_value = True
        
        select_reward = SelectReward()
        select_reward.setReward(player=1, card=card_mock, reward=[Resource.RED, Resource.CONSTRUCTION])
        
        # Action & Assert
        assert select_reward.canSelectReward(Resource.FOOD) is False
        pytest.raises(ValueError, select_reward.selectReward, Resource.FOOD)

    def test_state_representation(self) -> None:
        card_mock = Mock(spec=InterfaceCard)
        card_mock.canPutResources.return_value = True
        
        select_reward = SelectReward()
        select_reward.setReward(player=2, card=card_mock, reward=[Resource.RED, Resource.FOOD])
        
        state_str = select_reward.state()
        state = json.loads(state_str)
        
        assert state["player"] == 2
        assert "RED" in state["available_resources"]
        assert "FOOD" in state["available_resources"]