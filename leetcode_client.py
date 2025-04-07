import requests
import random
from typing import Dict, List, Optional

class LeetCodeClient:
    def __init__(self):
        self.base_url = "https://leetcode.com/api/problems/all/"
        self.problems = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.load_problems()
    
    def load_problems(self):
        """Load all problems from LeetCode API"""
        try:
            response = requests.get(self.base_url)
            if response.status_code == 200:
                data = response.json()
                self.problems = data.get('stat_status_pairs', [])
        except Exception as e:
            print(f"Error loading problems: {e}")
            self.problems = []
    
    def get_daily_problem(self, include_premium=False):
        """Get today's daily problem"""
        try:
            # Get the daily problem
            response = requests.get(
                "https://leetcode.com/graphql",
                json={
                    "query": """
                    query questionOfToday {
                        activeDailyCodingChallengeQuestion {
                            date
                            userStatus
                            link
                            question {
                                questionId
                                questionFrontendId
                                title
                                titleSlug
                                difficulty
                                isPaidOnly
                                topicTags {
                                    name
                                    slug
                                }
                            }
                        }
                    }
                    """
                },
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and 'activeDailyCodingChallengeQuestion' in data['data']:
                problem = data['data']['activeDailyCodingChallengeQuestion']
                if problem['question']['isPaidOnly'] and not include_premium:
                    # If it's a premium problem and we're not including premium, get a random non-premium problem
                    return self.get_random_problem(include_premium=False)
                
                return {
                    'title': problem['question']['title'],
                    'url': f"https://leetcode.com{problem['link']}",
                    'difficulty': problem['question']['difficulty'],
                    'category': problem['question']['topicTags'][0]['name'] if problem['question']['topicTags'] else 'Unknown',
                    'is_premium': problem['question']['isPaidOnly']
                }
            return None
        except Exception as e:
            print(f"Error getting daily problem: {e}")
            return None

    def get_random_problem(self, difficulty=None, category=None, include_premium=False):
        """Get a random problem with optional filters"""
        try:
            # Get all problems
            response = requests.get(
                "https://leetcode.com/api/problems/all/",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            # Filter problems based on criteria
            problems = [
                p for p in data['stat_status_pairs']
                if (not p['paid_only'] or include_premium) and  # Filter out premium problems unless include_premium is True
                (difficulty is None or p['difficulty']['level'] == {'Easy': 1, 'Medium': 2, 'Hard': 3}[difficulty]) and
                (category is None or any(tag['name'] == category for tag in p.get('tags', [])))
            ]
            
            if problems:
                problem = random.choice(problems)
                return {
                    'title': problem['stat']['question__title'],
                    'url': f"https://leetcode.com/problems/{problem['stat']['question__title_slug']}",
                    'difficulty': {1: 'Easy', 2: 'Medium', 3: 'Hard'}[problem['difficulty']['level']],
                    'category': problem.get('tags', [{'name': 'Unknown'}])[0]['name'],
                    'is_premium': problem['paid_only']
                }
            return None
        except Exception as e:
            print(f"Error getting random problem: {e}")
            return None
    
    def _get_difficulty_name(self, level: int) -> str:
        """Convert difficulty level to name"""
        difficulty_map = {
            1: 'Easy',
            2: 'Medium',
            3: 'Hard'
        }
        return difficulty_map.get(level, 'Unknown')
    
    def get_problem_categories(self) -> List[str]:
        """Get list of problem categories"""
        # This is a simplified version - in reality, you'd want to fetch this from the API
        return [
            'Array', 'String', 'Hash Table', 'Dynamic Programming', 'Math',
            'Sorting', 'Greedy', 'Depth-First Search', 'Binary Search',
            'Breadth-First Search', 'Tree', 'Matrix', 'Two Pointers',
            'Bit Manipulation', 'Binary Tree', 'Heap (Priority Queue)',
            'Stack', 'Graph', 'Prefix Sum', 'Simulation', 'Counting',
            'Backtracking', 'Sliding Window', 'Union Find', 'Linked List',
            'Monotonic Stack', 'Recursion', 'Divide and Conquer'
        ] 