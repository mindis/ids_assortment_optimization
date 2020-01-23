import os
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# TODO refactor plots et prettify them

OUTPUTS_FOLDER = 'outputs'
if not os.path.isdir(OUTPUTS_FOLDER):
    os.makedirs(OUTPUTS_FOLDER)


def act_optimally(belief, top_k):
    return np.argpartition(belief, -top_k)[-top_k:]


def print_regret(exp_results, true_preferences, assortment_size, n_steps):
    """
    :param n_steps:
    :param assortment_size:
    :param true_preferences:
    :param exp_results: dict of {agent_name_str: (observations, rewards)}
        with observations = [(assortment one hot size n+1, item_picked_index<=n)]
             rewards = [0., 1., 0., 0., ...]
    :return: plots and saves in OUTPUTS_FOLDER
    """
    # Expected rewards profile for optimal agent
    preferences_top = np.sort(true_preferences)[-(assortment_size + 1):]
    preferences_top = preferences_top / preferences_top.sum()
    expected_top_rewards = preferences_top[:assortment_size].sum() * np.ones(n_steps)
    expected_top_rewards = np.cumsum(expected_top_rewards)

    plt.figure()
    for agent_name, (_, rewards) in exp_results.items():
        rewards = np.cumsum(rewards)
        cumulative_regret = expected_top_rewards - rewards
        plt.plot(np.arange(n_steps), cumulative_regret, label=f"Regret curve for {agent_name} agent.")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(OUTPUTS_FOLDER, 'regret.png'))
    plt.close()


def print_actions(exp_results, true_preferences):

    plt.figure()
    preferences = true_preferences[:-1]
    preferences = preferences / preferences.sum()
    plt.scatter(np.arange(preferences.shape[0], dtype=int), preferences, label='preferences_normalized')
    for agent_name, (observations, _) in exp_results.items():
        item_proposals = defaultdict(int)

        for assortment, item_picked in observations:
            for item in assortment:
                item_proposals[item] += 1

        items, proposals = list(zip(*[(item, proposed_count) for item, proposed_count in item_proposals.items()]))
        proposals = np.array(proposals)
        proposals = proposals / proposals.sum()
        plt.scatter(items, proposals, label=f'proposals_normalized_probas for {agent_name} agent')

    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(OUTPUTS_FOLDER, 'proposals_vs_preferences.png'))
    plt.close()


def print_run(env, agent, h, observations, rews):
    """
    :param env:
    :param agent:
    :param h:
    :param observations:
    :param rews:
    :return:
    """
    # Parameters
    k = agent.assortment_size
    n = agent.n_items
    true_preferences = env.preferences

    # Actions selected
    item_proposals = defaultdict(int)
    item_picks = defaultdict(int)

    for assortment, item_picked in observations:
        for item in assortment:
            item_proposals[item] += 1
        item_picks[item_picked] += 1

    # Cumulated rewards vs top agent expectation
    plt.figure()
    preferences_top = np.sort(true_preferences)[-(k + 1):]
    assert len(preferences_top) == k + 1
    preferences_top = preferences_top / preferences_top.sum()
    expected_top_rewards = preferences_top[:k].sum() * np.ones(h)
    expected_top_rewards = np.cumsum(expected_top_rewards)
    plt.plot(np.arange(h), expected_top_rewards, label="expected top cumulated rewards")
    plt.plot(np.arange(h), np.cumsum(rews), label="agent cumulated rewards")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(OUTPUTS_FOLDER, 'rewards.png'))
    plt.close()

    plt.figure()
    items, proposals = list(zip(*[(item, proposed_count) for item, proposed_count in item_proposals.items()]))
    proposals = np.array(proposals) / h
    proposals = proposals / proposals.sum()
    plt.scatter(items, proposals, label='proposals_normalized_probas')
    preferences = true_preferences[:n]
    preferences = preferences / preferences.sum()
    plt.scatter(np.arange(n, dtype=int), preferences, label='preferences_normalized')
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(OUTPUTS_FOLDER, 'proposals_vs_preferences.png'))
    plt.close()

    plt.figure()
    items, picks = list(zip(*[(item, picked_count) for item, picked_count in item_picks.items()]))
    plt.scatter(items, np.array(picks) / h, label="actual_picks")
    true_preferences = env.preferences
    plt.scatter(np.arange(n + 1, dtype=int), true_preferences / true_preferences.sum(),
                label="picks_from_full_assortments")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(OUTPUTS_FOLDER, 'picks_vs_full_assortment.png'))
    plt.close()

    return
