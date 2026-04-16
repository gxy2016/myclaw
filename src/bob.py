"""
Bob's API Module
================

This module provides utility functions for the myclaw project.

Author: bob
Date: 2026-03-18
"""

from typing import List, Dict, Any
from datetime import datetime


def get_user_info(user_id: int) -> Dict[str, Any]:
    """
    Retrieve user information by user ID.
    
    This function simulates fetching user data from a database.
    In a real implementation, this would query a database or API.
    
    Args:
        user_id (int): The unique identifier of the user.
        
    Returns:
        Dict[str, Any]: A dictionary containing user information with the following keys:
            - user_id (int): The user's ID
            - name (str): The user's name
            - email (str): The user's email address
            - created_at (str): ISO format timestamp of when the user was created
            
    Example:
        >>> user = get_user_info(1)
        >>> print(user['name'])
        'Alice'
    """
    # Simulated user database
    users_db = {
        1: {"user_id": 1, "name": "Alice", "email": "alice@example.com"},
        2: {"user_id": 2, "name": "Bob", "email": "bob@example.com"},
        3: {"user_id": 3, "name": "Charlie", "email": "charlie@example.com"},
    }
    
    user = users_db.get(user_id, {})
    if user:
        user["created_at"] = datetime.now().isoformat()
    
    return user


def calculate_statistics(numbers: List[float]) -> Dict[str, float]:
    """
    Calculate basic statistics for a list of numbers.
    
    This function computes common statistical measures including
    mean, minimum, maximum, and sum of the input numbers.
    
    Args:
        numbers (List[float]): A list of numeric values to analyze.
        
    Returns:
        Dict[str, float]: A dictionary containing statistical measures:
            - count (int): Number of elements
            - sum (float): Sum of all elements
            - mean (float): Arithmetic mean
            - min (float): Minimum value
            - max (float): Maximum value
            
    Raises:
        ValueError: If the input list is empty.
        
    Example:
        >>> stats = calculate_statistics([1, 2, 3, 4, 5])
        >>> print(stats['mean'])
        3.0
    """
    if not numbers:
        raise ValueError("Input list cannot be empty")
    
    return {
        "count": len(numbers),
        "sum": sum(numbers),
        "mean": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers),
    }


if __name__ == "__main__":
    # Demo usage
    print("Bob's API Module - Demo")
    print("=" * 40)
    
    # Test get_user_info
    user = get_user_info(1)
    print(f"User Info: {user}")
    
    # Test calculate_statistics
    stats = calculate_statistics([10, 20, 30, 40, 50])
    print(f"Statistics: {stats}")
