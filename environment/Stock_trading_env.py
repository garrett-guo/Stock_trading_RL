import random
import json
import gym
from gym import spaces
import numpy as np
import pandas as pd

MAX_ACCOUNT_BALANCE = 1e10
MAX_NUM_SHARES = 1e10
MAX_SHARE_PRICE = 5000
MAX_VOLUME = 1000e8
MAX_AMOUNT = 3e10
MAX_STEPS = 20000
MAX_DAY_CHANGE = 1

INITIAL_ACCOUNT_BALANCE = 1000000


class Stock_trading(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, df, discrete):
        super(Stock_trading, self).__init__()

        self.df = df
        self.reward_range = (0, MAX_ACCOUNT_BALANCE)
        self.discrete = discrete
        # print('self.discrete in env:{}'.format(self.discrete))

        if self.discrete:
            self.action_space = spaces.Discrete(3)
        else:
            self.action_space = spaces.Box(low=np.array([0, 0]), high=np.array([3, 1]), dtype=np.float32)

        self.observation_space = spaces.Box(
            low=0, high=1, shape=(17,), dtype=np.float32)

        self.action_name = 'HOLD'
        self.trade_price = 0.0

    def _next_observation(self):
        obs = np.array([
            self.df.loc[self.current_step, 'open'] / MAX_SHARE_PRICE,
            self.df.loc[self.current_step, 'high'] / MAX_SHARE_PRICE,
            self.df.loc[self.current_step, 'low'] / MAX_SHARE_PRICE,
            self.df.loc[self.current_step, 'close'] / MAX_SHARE_PRICE,
            self.df.loc[self.current_step, 'volume'] / MAX_VOLUME,
            self.df.loc[self.current_step, 'amount'] / MAX_AMOUNT,
            self.df.loc[self.current_step, 'adjustflag'] / 10,
            self.df.loc[self.current_step, 'tradestatus'] / 1,
            self.df.loc[self.current_step, 'pctChg'] / 100,
            self.df.loc[self.current_step, 'peTTM'] / 1e4,
            self.df.loc[self.current_step, 'pbMRQ'] / 100,
            self.df.loc[self.current_step, 'psTTM'] / 100,
            self.df.loc[self.current_step, 'pctChg'] / 1e3,
            self.balance / MAX_ACCOUNT_BALANCE,
            self.max_net_wealth / MAX_ACCOUNT_BALANCE,
            self.shares_held / MAX_NUM_SHARES,
            self.cost_basis / MAX_SHARE_PRICE,
        ])
        return obs

    def _take_action(self, action):
        current_price = random.uniform(
            self.df.loc[self.current_step, "low"], self.df.loc[self.current_step, "high"])

        if self.discrete:
            action_type = action
        else:
            action_type = action[0]
            amount = action[1]

        if not self.df.loc[self.current_step,'tradestatus']:
            action_type = 3

        if action_type < 1:
            total_possible = int(self.balance / current_price)
            if self.discrete:
                shares_bought = int(total_possible)
            else:
                shares_bought = int(total_possible * amount)
            if shares_bought:
                self.action_name = 'BUY'
                self.trade_price = current_price
            else:
                self.action_name = 'HOLD'
            prev_cost = self.cost_basis * self.shares_held
            additional_cost = shares_bought * current_price

            self.balance -= additional_cost
            self.cost_basis = (prev_cost + additional_cost) / (self.shares_held + shares_bought) if self.shares_held + shares_bought !=0 else 0
            self.shares_held += shares_bought

        elif action_type < 2:
            if self.discrete:
                shares_sold = int(self.shares_held)
            else:
                shares_sold = int(self.shares_held * amount)
            if shares_sold:
                self.action_name = 'SELL'
                self.trade_price = current_price
            else:
                self.action_name = 'HOLD'

            prev_cost = self.cost_basis * self.shares_held
            addtional_revenue = shares_sold * current_price

            self.balance += addtional_revenue
            self.cost_basis = (prev_cost - addtional_revenue) / (
                        self.shares_held - shares_sold) if self.shares_held - shares_sold!=0 else 0
            self.shares_held -= shares_sold

        else:
            self.action_name = 'HOLD'

        self.net_wealth = self.balance + self.shares_held * self.df.loc[self.current_step, "close"]

        if self.net_wealth > self.max_net_wealth:
            self.max_net_wealth = self.net_wealth

        if self.shares_held == 0:
            self.cost_basis = 0

    def step(self, action):
        self.current_step += 1

        if self.current_step > len(self.df.loc[:, 'open'].values) - 1:
            self.current_step = 0

        self._take_action(action)
        done = False

        reward = (self.df.loc[self.current_step,'close'] - self.cost_basis)*self.shares_held / self.balance
        reward = -100 if reward <0 else 100*reward

        if self.net_wealth <= 0:
            done = True

        obs = self._next_observation()

        return obs, reward, done, {}

    def reset(self, new_df=None):
        # Reset the state of the environment to an initial state
        self.balance = INITIAL_ACCOUNT_BALANCE
        self.net_wealth = INITIAL_ACCOUNT_BALANCE
        self.max_net_wealth = INITIAL_ACCOUNT_BALANCE
        self.shares_held = 0
        self.cost_basis = 0

        if new_df:
            self.df = new_df

        self.current_step = 0

        return self._next_observation()

    def render(self, mode='human', close=False):
        profit = self.net_wealth - INITIAL_ACCOUNT_BALANCE
        print('-'*100)
        print('Step: {}'.format(self.current_step))
        print('Action:{} '.format(self.action_name))
        print('Balance:{}'.format(self.balance))
        print('Share(s): {} '.format(self.shares_held))
        print('Avg cost for held shares: {} '.format(self.cost_basis))
        print('Net wealth: {} (Max net wealth: {})'.format(self.net_wealth,self.max_net_wealth))
        print('Profit: {}'.format(profit))
        return (self.net_wealth,self.action_name)
