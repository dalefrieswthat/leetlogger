from typing import Dict, List
from datetime import datetime, timedelta
import json
import os

class StatisticsManager:
    def __init__(self):
        self.problems = []
        self.load_problems()
        self.dsa_patterns = {
            'Array/String': {
                'Binary Search': ['sorted array', 'search', 'find element'],
                'Two Pointers': ['two pointers', 'pair', 'sum', 'subarray'],
                'Dynamic Programming': ['number of ways', 'max/min', 'dependent decisions'],
                'Greedy': ['max/min', 'independent decisions'],
                'Backtracking': ['possible', 'combinations', 'permutations'],
                'Trie': ['prefix', 'word search'],
                'Stack': ['string manipulation', 'parentheses'],
                'Hash Map/Set': ['find element', 'duplicate', 'unique'],
                'Sliding Window': ['subarray', 'substring', 'window'],
                'Heap': ['max/min element', 'priority'],
                'Monotonic Stack': ['next greater', 'next smaller']
            },
            'Graph': {
                'BFS': ['shortest path', 'fewest steps', 'level order'],
                'DFS': ['connected components', 'cycle detection', 'path finding']
            },
            'Tree': {
                'BFS': ['level order', 'specific depth'],
                'DFS': ['inorder', 'preorder', 'postorder']
            },
            'Linked List': {
                'Fast and Slow Pointers': ['cycle detection', 'middle element'],
                'Reversal': ['reverse', 'modify']
            }
        }
    
    def load_problems(self):
        """Load problems from the JSON file"""
        try:
            if os.path.exists('problems.json'):
                with open('problems.json', 'r') as f:
                    self.problems = json.load(f)
        except Exception as e:
            print(f"Error loading problems: {e}")
            self.problems = []
    
    def save_problems(self):
        """Save problems to the JSON file"""
        try:
            with open('problems.json', 'w') as f:
                json.dump(self.problems, f, indent=4)
        except Exception as e:
            print(f"Error saving problems: {e}")
    
    def get_all_problems(self):
        """Return all problems"""
        return self.problems
    
    def add_problem(self, problem):
        """Add a new problem to the list"""
        self.problems.append(problem)
        self.save_problems()
    
    def get_completion_stats(self) -> Dict:
        """Get overall completion statistics"""
        total = len(self.problems)
        completed = sum(1 for p in self.problems if isinstance(p, dict) and p.get('completed', False))
        completion_rate = (completed / total * 100) if total > 0 else 0
        return {
            'total_problems': total,
            'completed_problems': completed,
            'completion_rate': completion_rate
        }
    
    def get_difficulty_stats(self) -> Dict:
        """Get statistics by difficulty level"""
        stats = {'Easy': 0, 'Medium': 0, 'Hard': 0}
        for problem in self.problems:
            if isinstance(problem, dict) and 'difficulty' in problem:
                difficulty = problem['difficulty']
                if difficulty in stats:
                    stats[difficulty] += 1
        return stats
    
    def get_pattern_stats(self) -> Dict:
        """Get statistics by DSA pattern"""
        patterns = {}
        for problem in self.problems:
            if isinstance(problem, dict) and 'category' in problem:
                category = problem['category']
                if category not in patterns:
                    patterns[category] = 0
                patterns[category] += 1
        return patterns
    
    def get_streak_stats(self) -> Dict:
        """Get streak statistics"""
        if not self.problems:
            return {'current_streak': 0, 'longest_streak': 0}
        
        # Sort problems by date
        sorted_problems = sorted(
            [p for p in self.problems if isinstance(p, dict) and 'date' in p],
            key=lambda x: datetime.fromisoformat(x['date']),
            reverse=True
        )
        
        current_streak = 0
        longest_streak = 0
        current_date = datetime.now().date()
        
        for problem in sorted_problems:
            problem_date = datetime.fromisoformat(problem['date']).date()
            if problem_date == current_date:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            elif problem_date == current_date - timedelta(days=1):
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
                current_date = problem_date
            else:
                break
        
        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak
        }
    
    def get_weekly_progress(self) -> Dict:
        """Get weekly progress statistics"""
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_problems = [
            p for p in self.problems
            if isinstance(p, dict) and 'date' in p and
            week_start <= datetime.fromisoformat(p['date']).date() <= today
        ]
        
        return {
            'problems_this_week': len(week_problems),
            'daily_completions': {
                i: len([p for p in week_problems
                       if datetime.fromisoformat(p['date']).weekday() == i])
                for i in range(7)
            }
        }
    
    def suggest_next_pattern(self) -> str:
        """Suggest the next DSA pattern to focus on based on completion stats"""
        pattern_stats = self.get_pattern_stats()
        if not pattern_stats:
            return "Start with Arrays or Strings problems"
        
        min_count = min(pattern_stats.values())
        suggested_patterns = [
            pattern for pattern, count in pattern_stats.items()
            if count == min_count
        ]
        return f"Focus on {', '.join(suggested_patterns)} problems next" 