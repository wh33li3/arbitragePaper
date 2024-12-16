import pandas as pd
import numpy as np
from typing import Dict


def check_arbitrage_opportunity(data_a: pd.Series, data_b: pd.Series, threshold: float = 0) -> int:
    """
    Check if there's an arbitrage opportunity between two price points.

    Args:
        data_a: Price data from exchange A
        data_b: Price data from exchange B
        threshold: Minimum profit percentage to consider

    Returns:
        1: Buy on exchange A, sell on B
        -1: Buy on exchange B, sell on A
        0: No opportunity
    """
    # Calculate potential profit percentages
    profit_buying_a = (data_b["price"] - data_a["low"]) / data_a["low"]  # Buy on A, sell on B
    profit_buying_b = (data_a["high"] - data_b["price"]) / data_b["price"]  # Buy on B, sell on A

    # Check if either profit percentage exceeds threshold
    if profit_buying_a > threshold:
        return 1  # Profitable to buy on A and sell on B
    elif profit_buying_b > threshold:
        return -1  # Profitable to buy on B and sell on A
    else:
        return 0  # No profitable opportunity


def calculate_profit_unitary(data_a: pd.Series, data_b: pd.Series, threshold: float = 0) -> float:
    """
    Calculate the profit in currency units.

    Args:
        data_a: Price data from exchange A
        data_b: Price data from exchange B
        threshold: Minimum profit percentage to consider

    Returns:
        Float representing profit in currency units
    """
    opportunity = check_arbitrage_opportunity(data_a, data_b, threshold)
    if opportunity == 1:
        return data_b["price"] - data_a["low"]
    elif opportunity == -1:
        return data_a["high"] - data_b["price"]
    else:
        return 0


def calculate_profit_percentage(data_a: pd.Series, data_b: pd.Series, threshold: float = 0) -> float:
    """
    Calculate the profit as a percentage.

    Args:
        data_a: Price data from exchange A
        data_b: Price data from exchange B
        threshold: Minimum profit percentage to consider

    Returns:
        Float representing profit percentage
    """
    opportunity = check_arbitrage_opportunity(data_a, data_b, threshold)
    if opportunity == 1:
        return (data_b["price"] - data_a["low"]) / data_a["low"]
    elif opportunity == -1:
        return (data_a["high"] - data_b["price"]) / data_b["price"]
    else:
        return 0


def create_opportunity_dict(data_a: pd.Series, data_b: pd.Series, threshold: float = 0) -> Dict:
    """
    Create a dictionary with the opportunity details.

    Args:
        data_a: Price data from exchange A
        data_b: Price data from exchange B
        threshold: Minimum profit percentage to consider

    Returns:
        Dictionary containing opportunity details
    """
    return {
        "timestamp": data_b.name,
        "type": check_arbitrage_opportunity(data_a, data_b, threshold),
        "profit_unitary": calculate_profit_unitary(data_a, data_b, threshold),
        "profit_percentage": calculate_profit_percentage(data_a, data_b, threshold),
        "price_a_high": data_a["high"],
        "price_a_low": data_a["low"],
        "price_b": data_b["price"],
        "volume_a": data_a["Volume BTC"],
        "volume_b": data_b["volume"],
        "threshold": threshold
    }


def find_opportunities(df_a: pd.DataFrame, df_b: pd.DataFrame, threshold: float = 0) -> pd.DataFrame:
    """
    Find arbitrage opportunities between two exchanges.

    Args:
        df_a: DataFrame from exchange A
        df_b: DataFrame from exchange B
        threshold: Minimum profit percentage to consider

    Returns:
        DataFrame containing all found opportunities
    """
    opportunities = []

    def find_closest_timestamp(target_time, time_series):
        return time_series.iloc[np.abs(time_series - target_time).argmin()]

    index = 0
    for _, row_b in df_b.iterrows():
        closest_time_a = find_closest_timestamp(row_b['timestamp'], df_a['timestamp'])
        row_a = df_a[df_a['timestamp'] == closest_time_a].iloc[0]
        index += 1

        opportunity_type = check_arbitrage_opportunity(row_a, row_b, threshold)
        if opportunity_type != 0:
            opportunity = create_opportunity_dict(row_a, row_b, threshold)
            opportunities.append(opportunity)
        if index % 1000 == 0:
            print(f"Processed {index} rows")

    return pd.DataFrame(opportunities)