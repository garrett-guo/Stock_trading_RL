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
# MAX_OPEN_POSITIONS = 5
MAX_STEPS = 20000
MAX_DAY_CHANGE = 1

INITIAL_ACCOUNT_BALANCE = 1000000


class Stock_trading(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, df, discrete=False):
        super(Stock_trading, self).__init__()

        self.df = df
        self.reward_range = (0, MAX_ACCOUNT_BALANCE)
        self.discrete = discrete

        if self.discrete:
            self.action_space = spaces.Discrete(3)
        else:
            self.action_space = spaces.Box(low=np.array([0, 0]), high=np.array([3, 1]), dtype=np.float32)

        self.observation_space = spaces.Box(
            low=0, high=1, shape=(19,), dtype=np.float32)

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
            self.max_net_worth / MAX_ACCOUNT_BALANCE,
            self.shares_held / MAX_NUM_SHARES,
            self.cost_basis / MAX_SHARE_PRICE,
            self.total_shares_sold / MAX_NUM_SHARES,
            self.total_sales_value / (MAX_NUM_SHARES * MAX_SHARE_PRICE),
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

        if action_type < 1:
            total_possible = int(self.balance / current_price)
            if self.discrete:
                shares_bought = int(total_possible)
            else:
                shares_bought = int(total_possible * amount)
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
            self.balance += shares_sold * current_price
            self.shares_held -= shares_sold
            self.total_shares_sold += shares_sold
            self.total_sales_value += shares_sold * current_price

        self.net_worth = self.balance + self.shares_held * self.df.loc[self.current_step, "close"]

        if self.net_worth > self.max_net_worth:
            self.max_net_worth = self.net_worth

        if self.shares_held == 0:
            self.cost_basis = 0

    def step(self, action):
        self.current_step += 1

        self._take_action(action)
        done = False

        if self.current_step > len(self.df.loc[:, 'open'].values) - 1:
            self.current_step = 0  # loop training

        delay_modifier = (self.current_step / MAX_STEPS)

        reward = self.net_worth - INITIAL_ACCOUNT_BALANCE
        reward = 1 if reward > 0 else -100

        if self.net_worth <= 0:
            done = True

        obs = self._next_observation()

        return obs, reward, done, {}

    def reset(self, new_df=None):
        # Reset the state of the environment to an initial state
        self.balance = INITIAL_ACCOUNT_BALANCE
        self.net_worth = INITIAL_ACCOUNT_BALANCE
        self.max_net_worth = INITIAL_ACCOUNT_BALANCE
        self.shares_held = 0
        self.cost_basis = 0
        self.total_shares_sold = 0
        self.total_sales_value = 0

        if new_df:
            self.df = new_df

        self.current_step = 0

        return self._next_observation()

    def render(self, mode='human', close=False):
        profit = self.net_worth - INITIAL_ACCOUNT_BALANCE
        print('-'*30)
        print('Step: {}'.format(self.current_step))
        print('Balance: {}',format(self.balance))
        print('Shares held: {} (Total sold: {})'.format(self.shares_held,self.total_shares_sold))
        print('Avg cost for held shares: {} (Total sales value: {})'.format(self.cost_basis,self.total_sales_value))
        print('Net worth: {} (Max net worth: {})'.format(self.net_worth,self.max_net_worth))
        print('Profit: {}'.format(profit))
        return (profit)
