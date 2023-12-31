import streamlit as st
import pandas as pd
import numpy as np

# Set defaults and generate random draws
np.random.seed(676732)
n = 200_000

@st.cache_data
def roll_base_dice(n):
    d6 = np.random.randint(1, 7, (n, 6))
    d12 = np.random.randint(0, 12, (n, 2))
    return d6, d12

d6, d12 = roll_base_dice(n)
target_list = list(range(11, 23))
n_success_dice_list = list(range(1, 6))


def roll(n_success_dice, d12=d12, d6=d6):
    """
    Rolls a set of feature dice and returns the sum of the rolls.

    Parameters:
        n_success_dice (int): The number of feature dice to roll.

    Returns:
        numpy.ndarray: An array containing the sum of the rolls.
    """
    success_sum = d6[:, 0:n_success_dice].sum(axis=1).reshape(-1, 1)
    feat_die = d12[:, 0:1].clip(0, 10)
    result = success_sum + feat_die
    return result


def p_success(target, n_success_dice, miserable=False, d12=d12, d6=d6):
    """
    Calculates the probability of success of a roll given a targer number.

    Parameters:
        target (int): The target number that needs to be rolled on the dice.
        n_success_dice (int): The number of succes dice available.

    Returns:
        float: The probability of success.
    """
    successes = (d12[:, 0:1]==11) | (roll(n_success_dice, d12=d12, d6=d6)>=target)
    if miserable:
        successes[np.where(d12[:, 0:1]==0)]=False
    return f"{successes.mean():.4f}"


def success_table(
        n_success_dice_list=n_success_dice_list,
        target_list=target_list,
        roll = 'Normal',
        weary=False,
        miserable=False
        ):
    # Resolve options
    if roll == 'Favored':
        feat_die = d12.max(axis=1).reshape(-1, 1)
    elif roll == 'Ill-favored':
        feat_die = d12.min(axis=1).reshape(-1, 1)
    else:
        feat_die = d12[:, 0:1]
    
    success_dice = d6.copy()
    if weary:
        success_dice[np.where(success_dice<=3)]=0

    # Calculate table
    table_data = [[p_success(target, n_feat_dice, d6=success_dice, d12=feat_die, miserable=miserable)
                   for n_feat_dice in n_success_dice_list] for target in target_list]
    df = pd.DataFrame(table_data, columns=n_success_dice_list, index=target_list)
    df.index.name = "Target number"
    # df.style.set_caption('Probability of success by number of feat dice')
    return df

## Dashboard proper

st.title('The One Ring rolls')

st.write("See [The One Ring](https://freeleaguepublishing.com/en/games/the-one-ring/) RPG game.")

roll_type = st.selectbox(
     'Feat roll type',
     ('Normal', 'Favored', 'Ill-favored')
)

weary = st.checkbox('Weary')
miserable = st.checkbox('Miserable')
st.write("**Probability of success by number of success dice**")
st.write(
    success_table(
        roll=roll_type,
        weary=weary,
        miserable=miserable
    )
)
