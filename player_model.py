import os
import torch
from torch import nn
import torch.nn.functional as F
import numpy as np
from torch.optim import Adam

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class AdvantageNetwork(nn.Module):
    def __init__(self, state_dim, action_dim, hidden_dim=64):
        super().__init__()
        
        # Define your network layers here
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.out = nn.Linear(hidden_dim, action_dim)
        
        # Initialization of weights could be beneficial
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                m.bias.data.fill_(0.01)

    def forward(self, state):
        x = state

        # Ensure that the state is a tensor. If it's an array, convert it to a tensor.
        if not isinstance(x, torch.Tensor):
            x = torch.tensor(x, dtype=torch.float32)
        
        # The operations inside the forward method are executed on the GPU if available
        x = x.to(device)

        # Apply the first fully connected layer with ReLU activation
        x = F.relu(self.fc1(x))

        # Apply the second fully connected layer with ReLU activation
        x = F.relu(self.fc2(x))

        # Apply the output layer (no activation function)
        advantages = self.out(x)
        
        return advantages




class StrategyNetwork(nn.Module):
    def __init__(self, state_dim, action_dim, hidden_dim=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim),
            nn.Softmax(dim=-1)
        )

    def forward(self, state):
        return self.net(state)


class DeepCFR:
    def __init__(self, state_dim, action_dim, lr=1e-3):
        self.adv_net = AdvantageNetwork(state_dim, action_dim)
        self.strat_net = StrategyNetwork(state_dim, action_dim)

        self.optimizer_adv = Adam(self.adv_net.parameters(), lr=lr)
        self.optimizer_strat = Adam(self.strat_net.parameters(), lr=lr)

        self.states = []
        self.advantages = []
        self.strategies = []

    def get_strategy(self, state):
        with torch.no_grad():
            return self.strat_net(state)

    def get_advantage(self, state):
        with torch.no_grad():
            return self.adv_net(state)

    def traverse_game_tree(self, game):
        # Traverse the game tree, collect states, compute advantages, and accumulate strategies
        # This is a recursive function that traverses all the nodes of the game tree
        pass

    def update(self):
        # Update the Advantage network
        states_tensor = torch.stack(self.states)
        advantages_tensor = torch.stack(self.advantages)
        self.optimizer_adv.zero_grad()
        loss_adv = ((self.adv_net(states_tensor) - advantages_tensor)**2).mean()
        loss_adv.backward()
        self.optimizer_adv.step()

        # Update the Strategy network
        states_tensor = torch.stack(self.states)
        strategies_tensor = torch.stack(self.strategies)
        self.optimizer_strat.zero_grad()
        loss_strat = ((self.strat_net(states_tensor) - strategies_tensor)**2).mean()
        loss_strat.backward()
        self.optimizer_strat.step()

        # Clear the states, advantages, and strategies
        self.states = []
        self.advantages = []
        self.strategies = []




class DRLPolicyNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(100, 256),  # Assume 100 features for the game state
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 10)   # Assume 10 possible actions
        )

    def forward(self, x):
        return F.softmax(self.layers(x), dim=1)

class MCTS:
    def __init__(self):
        # Initialize the search tree here
        pass

    def search(self, game_state, policy_network):
        # Run MCTS using the given policy network and return an action
        pass

class PlayerModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.drl_policy_network = DRLPolicyNetwork()
        self.cfr_component = DeepCFR()
        self.mcts_component = MCTS()

    def forward(self, x):
        return self.drl_policy_network(x)

    def cfr_update(self, game_state, action_taken):
        self.cfr_component.update(game_state, action_taken)

    def mcts_decision(self, game_state):
        return self.mcts_component.search(game_state, self.drl_policy_network)



class PlayerModelManager:
    def __init__(self, directory, num_models):
        self.directory = directory
        self.num_models = num_models

        # Create directory if it does not exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Initialize the player models
        self.models = [PlayerModel() for _ in range(num_models)]

    def save_models(self):
        for i, model in enumerate(self.models):
            torch.save(model.state_dict(), os.path.join(self.directory, f'model_{i}.pth'))

    def load_models(self):
        for i in range(self.num_models):
            model_path = os.path.join(self.directory, f'model_{i}.pth')
            if os.path.exists(model_path):
                self.models[i].load_state_dict(torch.load(model_path))
            else:
                print(f"No model found at {model_path}")


class Model:
    def __init__(self, name):
        self.name = name

    def predict(self, state):
        # Implement the prediction logic here.
        # This is just a placeholder.
        pass
