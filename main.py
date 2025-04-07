import sys
import json
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QLabel, QCheckBox, QTextEdit, QTabWidget,
                           QComboBox, QHBoxLayout, QMessageBox, QGridLayout,
                           QProgressBar, QGroupBox, QFrame, QDialog, QListWidget,
                           QDialogButtonBox, QFormLayout, QLineEdit)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPalette, QColor, QFont, QIcon
import requests
import schedule
import time
from threading import Thread
from leetcode_client import LeetCodeClient
from notification_manager import NotificationManager
from statistics_manager import StatisticsManager
from backup_manager import BackupManager
import os
import shutil

class StyledButton(QPushButton):
    def __init__(self, text, color="#4CAF50"):
        super().__init__(text)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self._adjust_color(color, 20)};
            }}
            QPushButton:pressed {{
                background-color: {self._adjust_color(color, -20)};
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(32)
    
    def _adjust_color(self, color, amount):
        """Adjust color brightness by amount"""
        r = int(color[1:3], 16) + amount
        g = int(color[3:5], 16) + amount
        b = int(color[5:7], 16) + amount
        return f"#{max(0, min(255, r)):02x}{max(0, min(255, g)):02x}{max(0, min(255, b)):02x}"

class StyledGroupBox(QGroupBox):
    def __init__(self, title):
        super().__init__(title)
        self.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: black;
                font-weight: bold;
            }
        """)

class StyledComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 2px solid #4CAF50;
                border-radius: 4px;
                padding: 8px 15px;
                min-width: 150px;
                color: #333;
                font-size: 14px;
            }
            QComboBox:hover {
                border-color: #45a049;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #4CAF50;
                selection-background-color: #4CAF50;
                selection-color: white;
                background-color: white;
                padding: 5px;
            }
        """)
        self.setMinimumHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class EditProblemDialog(QDialog):
    def __init__(self, problem_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Problem")
        self.setModal(True)
        self.problem_data = problem_data
        
        layout = QFormLayout(self)
        
        self.title_edit = QLineEdit(problem_data['title'])
        layout.addRow("Title:", self.title_edit)
        
        self.url_edit = QLineEdit(problem_data['url'])
        layout.addRow("URL:", self.url_edit)
        
        self.difficulty_edit = QComboBox()
        self.difficulty_edit.addItems(['Easy', 'Medium', 'Hard'])
        self.difficulty_edit.setCurrentText(problem_data['difficulty'])
        layout.addRow("Difficulty:", self.difficulty_edit)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setText(problem_data['notes'])
        layout.addRow("Notes:", self.notes_edit)
        
        self.completed_checkbox = QCheckBox("Completed")
        self.completed_checkbox.setChecked(problem_data['completed'])
        layout.addRow("", self.completed_checkbox)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def get_updated_data(self):
        return {
            'title': self.title_edit.text(),
            'url': self.url_edit.text(),
            'difficulty': self.difficulty_edit.currentText(),
            'notes': self.notes_edit.toPlainText(),
            'completed': self.completed_checkbox.isChecked(),
            'date': self.problem_data['date']
        }

class DSAProblemTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LeetLogger")
        self.setMinimumWidth(800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Initialize managers
        self.notification_manager = NotificationManager()
        self.statistics_manager = StatisticsManager()
        self.backup_manager = BackupManager()
        self.leetcode_client = LeetCodeClient()  # Initialize LeetCode client
        
        # Load problems from file
        self.problems = []  # Initialize as empty list
        self.load_problems()
        
        # Create tabs
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                background-color: white;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #ddd;
                padding: 8px 16px;
                margin-right: 2px;
                color: black;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: none;
                color: black;
                font-weight: bold;
            }
            QLabel {
                color: black;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(tabs)
        
        # Create and add tabs
        daily_tab = self.create_daily_tab()
        progress_tab = self.create_progress_tab()
        
        # Set tab text color explicitly
        tabs.setTabText(tabs.addTab(daily_tab, ""), "Daily Problem")
        tabs.setTabText(tabs.addTab(progress_tab, ""), "Progress")
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        backup_button = StyledButton("Backup Data", "#FF9800")
        backup_button.clicked.connect(self.create_backup)
        button_layout.addWidget(backup_button)
        
        manage_button = StyledButton("Manage Problems", "#9C27B0")
        manage_button.clicked.connect(self.show_problem_manager)
        button_layout.addWidget(manage_button)
        
        main_layout.addLayout(button_layout)
        
        # Set window background and text colors
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            QWidget {
                color: black;
            }
            QTabWidget {
                color: black;
            }
            QLabel {
                color: black;
            }
        """)
        
        # Set up timers and threads
        self.setup_reminder_timer()
        
        self.scheduler_thread = Thread(target=self.run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_statistics)
        self.stats_timer.start(60000)  # Update every minute
        
        # Set application icon
        icon_path = os.path.abspath("icon.png")
        if os.path.exists(icon_path):
            self.app_icon = QIcon(icon_path)
            self.setWindowIcon(self.app_icon)
            # Copy icon to resources for notifications
            os.makedirs("resources", exist_ok=True)
            shutil.copy2(icon_path, "resources/icon.png")
    
    def create_daily_tab(self):
        daily_tab = QWidget()
        daily_layout = QVBoxLayout(daily_tab)
        daily_layout.setSpacing(15)
        
        # Set daily tab styles
        daily_tab.setStyleSheet("""
            QWidget {
                background-color: white;
                color: black;
            }
            QLabel {
                color: black;
                font-weight: bold;
            }
            QGroupBox {
                color: black;
                font-weight: bold;
            }
            QGroupBox::title {
                color: black;
                font-weight: bold;
            }
        """)
        
        # Problem selection controls
        controls_frame = QFrame()
        controls_frame.setFrameShape(QFrame.Shape.StyledPanel)
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 20px;
            }
            QLabel {
                color: black;
                font-weight: bold;
            }
            QGroupBox {
                color: black;
                font-weight: bold;
            }
            QGroupBox::title {
                color: black;
                font-weight: bold;
            }
        """)
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setSpacing(20)
        
        # Difficulty Dropdown
        difficulty_group = QGroupBox("Difficulty")
        difficulty_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: #333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        difficulty_layout = QVBoxLayout(difficulty_group)
        self.difficulty_combo = StyledComboBox()
        self.difficulty_combo.addItems(["Easy", "Medium", "Hard"])
        self.difficulty_combo.setCurrentText("Medium")
        difficulty_layout.addWidget(self.difficulty_combo)
        controls_layout.addWidget(difficulty_group)
        
        # Category Dropdown
        category_group = QGroupBox("Category")
        category_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: #333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        category_layout = QVBoxLayout(category_group)
        self.category_combo = StyledComboBox()
        self.category_combo.addItems([
            "Arrays", "Strings", "Linked Lists", "Trees", "Graphs",
            "Dynamic Programming", "Backtracking", "Sorting", "Searching",
            "Math", "Bit Manipulation", "Stack", "Queue", "Heap",
            "Hash Table", "Binary Search", "Two Pointers", "Sliding Window",
            "Greedy", "Divide and Conquer"
        ])
        category_layout.addWidget(self.category_combo)
        controls_layout.addWidget(category_group)
        
        # Get Problem Button
        self.get_problem_btn = StyledButton("Get Daily Problem", "#2196F3")
        self.get_problem_btn.clicked.connect(self.get_daily_problem)
        controls_layout.addWidget(self.get_problem_btn)
        
        daily_layout.addWidget(controls_frame)
        
        # Problem display frame
        problem_frame = QFrame()
        problem_frame.setFrameShape(QFrame.Shape.StyledPanel)
        problem_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 20px;
            }
            QLabel {
                color: black;
                font-size: 14px;
            }
            QLabel#problemTitle {
                color: black;
                font-size: 18px;
                font-weight: bold;
            }
            QLabel#problemLink {
                color: black;
                font-size: 14px;
                text-decoration: underline;
            }
        """)
        problem_layout = QVBoxLayout(problem_frame)
        
        self.problem_title = QLabel("No problem selected")
        self.problem_title.setObjectName("problemTitle")
        self.problem_url = QLabel()
        self.problem_url.setObjectName("problemLink")
        self.problem_url.setOpenExternalLinks(True)
        
        problem_layout.addWidget(self.problem_title)
        problem_layout.addWidget(self.problem_url)
        
        self.difficulty_label = QLabel()
        problem_layout.addWidget(self.difficulty_label)
        
        self.completed_checkbox = QCheckBox("I've attempted this problem")
        self.completed_checkbox.stateChanged.connect(self.on_completion_changed)
        problem_layout.addWidget(self.completed_checkbox)
        
        self.notes_text = QTextEdit()
        self.notes_text.setPlaceholderText("Add your notes about this problem here...")
        self.notes_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                background-color: white;
            }
        """)
        problem_layout.addWidget(self.notes_text)
        
        save_button = StyledButton("Save Notes", "#4CAF50")
        save_button.clicked.connect(self.save_notes)
        problem_layout.addWidget(save_button)
        
        daily_layout.addWidget(problem_frame)
        
        return daily_tab
    
    def create_progress_tab(self):
        progress_tab = QWidget()
        progress_layout = QVBoxLayout(progress_tab)
        progress_layout.setSpacing(15)
        
        # Set progress tab styles
        progress_tab.setStyleSheet("""
            QWidget {
                background-color: white;
                color: black;
            }
            QLabel {
                color: black;
                font-weight: bold;
            }
            QGroupBox {
                color: black;
                font-weight: bold;
            }
            QGroupBox::title {
                color: black;
                font-weight: bold;
            }
        """)
        
        # Overall Progress Section
        progress_group = StyledGroupBox("Overall Progress")
        progress_group_layout = QVBoxLayout()
        progress_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: black;
                font-weight: bold;
            }
            QLabel {
                color: black;
                font-weight: bold;
            }
            QProgressBar {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                text-align: center;
                background-color: #E0E0E0;
                color: black;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 4px;
            }
        """)
        
        completion_stats = self.statistics_manager.get_completion_stats()
        self.completion_label = QLabel(
            f"Problems Completed: {completion_stats['completed_problems']}/{completion_stats['total_problems']} "
            f"({completion_stats['completion_rate']:.1f}%)"
        )
        self.completion_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
        progress_group_layout.addWidget(self.completion_label)
        
        # Streak Section
        streak_group = StyledGroupBox("Streak")
        streak_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: black;
                font-weight: bold;
            }
            QLabel {
                color: black;
            }
        """)
        streak_layout = QVBoxLayout()
        
        streak_stats = self.statistics_manager.get_streak_stats()
        self.streak_label = QLabel(
            f"Current Streak: {streak_stats['current_streak']} days\n"
            f"Longest Streak: {streak_stats['longest_streak']} days"
        )
        self.streak_label.setStyleSheet("font-size: 14px; color: black;")
        streak_layout.addWidget(self.streak_label)
        streak_group.setLayout(streak_layout)
        progress_group_layout.addWidget(streak_group)
        
        # Difficulty Stats
        difficulty_group = StyledGroupBox("Difficulty Breakdown")
        difficulty_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: black;
                font-weight: bold;
            }
            QLabel {
                color: black;
                font-weight: bold;
            }
            QProgressBar {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                text-align: center;
                background-color: #E0E0E0;
                color: black;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 4px;
            }
        """)
        difficulty_layout = QVBoxLayout()
        
        difficulty_stats = self.statistics_manager.get_difficulty_stats()
        for level, count in difficulty_stats.items():
            level_layout = QHBoxLayout()
            level_label = QLabel(f"{level}:")
            level_label.setStyleSheet("font-weight: bold;")
            level_layout.addWidget(level_label)
            progress = QProgressBar()
            progress.setMaximum(completion_stats['completed_problems'] or 1)
            progress.setValue(count)
            level_layout.addWidget(progress)
            count_label = QLabel(str(count))
            count_label.setStyleSheet("font-weight: bold;")
            level_layout.addWidget(count_label)
            difficulty_layout.addLayout(level_layout)
        
        difficulty_group.setLayout(difficulty_layout)
        progress_group_layout.addWidget(difficulty_group)
        
        # Pattern Stats
        pattern_group = StyledGroupBox("DSA Pattern Progress")
        pattern_layout = QVBoxLayout()
        
        pattern_stats = self.statistics_manager.get_pattern_stats()
        for category, patterns in pattern_stats.items():
            category_label = QLabel(f"\n{category}:")
            category_label.setStyleSheet("font-weight: bold; color: #333;")
            pattern_layout.addWidget(category_label)
            
            for pattern, count in patterns.items():
                pattern_label = QLabel(f"  {pattern}: {count} problems")
                pattern_label.setStyleSheet("color: #666;")
                pattern_layout.addWidget(pattern_label)
        
        pattern_group.setLayout(pattern_layout)
        progress_group_layout.addWidget(pattern_group)
        
        # Weekly Progress
        weekly_group = StyledGroupBox("Weekly Progress")
        weekly_layout = QVBoxLayout()
        
        weekly_stats = self.statistics_manager.get_weekly_progress()
        weekly_label = QLabel(f"Problems this week: {weekly_stats['problems_this_week']}")
        weekly_label.setStyleSheet("font-weight: bold;")
        weekly_layout.addWidget(weekly_label)
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day, count in weekly_stats['daily_completions'].items():
            day_layout = QHBoxLayout()
            day_label = QLabel(f"{days[day]}:")
            day_label.setStyleSheet("font-weight: bold;")
            day_layout.addWidget(day_label)
            progress = QProgressBar()
            progress.setMaximum(weekly_stats['problems_this_week'] or 1)
            progress.setValue(count)
            day_layout.addWidget(progress)
            count_label = QLabel(str(count))
            count_label.setStyleSheet("font-weight: bold;")
            day_layout.addWidget(count_label)
            weekly_layout.addLayout(day_layout)
        
        weekly_group.setLayout(weekly_layout)
        progress_group_layout.addWidget(weekly_group)
        
        # Next Pattern Suggestion
        suggestion_group = StyledGroupBox("Next Pattern to Focus On")
        suggestion_layout = QVBoxLayout()
        
        self.suggestion_label = QLabel(self.statistics_manager.suggest_next_pattern())
        self.suggestion_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        suggestion_layout.addWidget(self.suggestion_label)
        
        suggestion_group.setLayout(suggestion_layout)
        progress_group_layout.addWidget(suggestion_group)
        
        progress_group.setLayout(progress_group_layout)
        progress_layout.addWidget(progress_group)
        
        return progress_tab
    
    def update_statistics(self):
        """Update all statistics displays"""
        # Update completion stats
        completion_stats = self.statistics_manager.get_completion_stats()
        self.completion_label.setText(
            f"Problems Completed: {completion_stats['completed_problems']}/{completion_stats['total_problems']} "
            f"({completion_stats['completion_rate']:.1f}%)"
        )
        
        # Update streak stats
        streak_stats = self.statistics_manager.get_streak_stats()
        self.streak_label.setText(
            f"Current Streak: {streak_stats['current_streak']} days\n"
            f"Longest Streak: {streak_stats['longest_streak']} days"
        )
        
        # Update suggestion
        self.suggestion_label.setText(self.statistics_manager.suggest_next_pattern())
    
    def load_problems(self):
        """Load problems from the JSON file"""
        try:
            with open('problems.json', 'r') as f:
                data = json.load(f)
                # Ensure data is a list
                self.problems = data if isinstance(data, list) else []
        except FileNotFoundError:
            self.problems = []
        except json.JSONDecodeError:
            self.problems = []
            
    def save_problems(self):
        """Save problems to JSON file"""
        # Ensure self.problems is a list
        if not isinstance(self.problems, list):
            self.problems = []
        with open('problems.json', 'w') as f:
            json.dump(self.problems, f, indent=4)
        self.update_statistics()
        self.backup_manager.create_backup()  # Create backup after saving
        self.backup_manager.cleanup_old_backups()  # Clean up old backups
    
    def update_daily_problem(self):
        difficulty = self.difficulty_combo.currentText()
        topic = self.category_combo.currentText()
        
        if difficulty == 'Any':
            difficulty = None
        if topic == 'Any':
            topic = None
            
        problem = self.leetcode_client.get_random_problem(difficulty, topic)
        
        if problem['paid_only']:
            QMessageBox.warning(self, "Premium Problem", 
                              "This is a premium problem. You might need a LeetCode subscription to access it.")
        
        self.problem_title.setText(f"Today's Problem: {problem['title']}")
        self.problem_url.setText(f'<a href="{problem["url"]}">{problem["url"]}</a>')
        self.difficulty_label.setText(f"Difficulty: {problem['difficulty']}")
        self.completed_checkbox.setChecked(False)
        self.notes_text.clear()
        
        # Send notification for new problem
        self.notification_manager.send_daily_problem_notification(
            problem['title'],
            problem['url']
        )
    
    def on_completion_changed(self, state):
        if state == Qt.CheckState.Checked.value:
            problem_title = self.problem_title.text().replace("Today's Problem: ", "")
            self.notification_manager.send_completion_notification(problem_title)
            self.update_statistics()  # Update statistics when problem is completed
    
    def check_reminder(self):
        # Check if it's after 6 PM and the problem hasn't been completed
        current_hour = datetime.now().hour
        if current_hour >= 18 and not self.completed_checkbox.isChecked():
            self.notification_manager.send_reminder_notification()
    
    def save_notes(self):
        current_problem = {
            'title': self.problem_title.text().replace("Today's Problem: ", ""),
            'url': self.problem_url.text().replace('<a href="', '').split('">')[0],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'difficulty': self.difficulty_label.text().replace("Difficulty: ", ""),
            'completed': self.completed_checkbox.isChecked(),
            'notes': self.notes_text.toPlainText()
        }
        
        self.problems.append(current_problem)
        self.save_problems()
        
        QMessageBox.information(self, "Success", "Your progress has been saved!")
    
    def run_scheduler(self):
        schedule.every().day.at("09:00").do(self.update_daily_problem)
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def create_backup(self):
        if self.backup_manager.create_backup():
            QMessageBox.information(self, "Success", "Backup created successfully!")
        else:
            QMessageBox.warning(self, "Error", "Failed to create backup.")
    
    def show_problem_manager(self):
        """Show the problem manager dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Problem Manager")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Problem list
        problem_list = QListWidget()
        problems = self.statistics_manager.get_all_problems()
        for problem in problems:
            if isinstance(problem, dict):
                problem_list.addItem(f"{problem['title']} ({problem['date']})")
            else:
                problem_list.addItem(str(problem))
        
        layout.addWidget(problem_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        load_button = QPushButton("Load Selected")
        load_button.clicked.connect(lambda: self.load_selected_problem(problem_list, dialog))
        button_layout.addWidget(load_button)
        
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(lambda: self.delete_selected_problem(problem_list))
        button_layout.addWidget(delete_button)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def load_selected_problem(self, problem_list, dialog):
        current_row = problem_list.currentRow()
        if current_row >= 0:
            selected_problem = self.problems[current_row]
            self.problem_title.setText(f"Today's Problem: {selected_problem['title']}")
            self.problem_url.setText(f'<a href="{selected_problem["url"]}">{selected_problem["url"]}</a>')
            self.difficulty_label.setText(f"Difficulty: {selected_problem['difficulty']}")
            self.completed_checkbox.setChecked(selected_problem['completed'])
            self.notes_text.setText(selected_problem['notes'])
            self.difficulty_combo.setCurrentText(selected_problem['difficulty'])
            self.category_combo.setCurrentText(selected_problem['category'])
            self.save_problems()
            QMessageBox.information(self, "Success", "Selected problem loaded successfully!")
    
    def delete_selected_problem(self, problem_list):
        current_row = problem_list.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(
                self, 'Confirm Delete',
                'Are you sure you want to delete this problem?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                del self.problems[current_row]
                self.save_problems()
                problem_list.takeItem(current_row)
    
    def get_daily_problem(self):
        """Get and display the daily problem"""
        try:
            problem = self.leetcode_client.get_daily_problem(include_premium=False)  # Set to False to exclude premium problems
            if problem:
                self.problem_title.setText(f"Today's Problem: {problem['title']}")
                self.problem_url.setText(f'<a href="{problem["url"]}">{problem["url"]}</a>')
                self.difficulty_label.setText(f"Difficulty: {problem['difficulty']}")
                self.completed_checkbox.setChecked(False)
                self.notes_text.clear()
                self.difficulty_combo.setCurrentText(problem['difficulty'])
                self.category_combo.setCurrentText(problem['category'])
                
                # Send notification
                self.notification_manager.send_daily_problem_notification(problem['title'], problem['url'])
            else:
                QMessageBox.warning(self, "Error", "Could not fetch daily problem")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to get daily problem: {e}")

    def load_saved_data(self):
        try:
            if os.path.exists("problems.json"):
                with open("problems.json", "r") as f:
                    data = json.load(f)
                    if data:
                        self.problem_title.setText(data.get("title", "No problem selected"))
                        self.problem_url.setText(data.get("url", ""))
                        self.notes_text.setText(data.get("notes", ""))
                        self.difficulty_combo.setCurrentText(data.get("difficulty", "Medium"))
                        self.category_combo.setCurrentText(data.get("category", "Arrays"))
        except Exception as e:
            print(f"Error loading saved data: {e}")

    def save_current_state(self):
        try:
            # Get the current problem data
            title = self.problem_title.text()
            url = self.problem_url.text()
            
            # Only save if we have valid data
            if title and url and title != "No problem selected":
                data = {
                    "title": title.replace("Today's Problem: ", ""),
                    "url": url.split('href="')[1].split('">')[0] if 'href="' in url else url,
                    "notes": self.notes_text.toPlainText(),
                    "difficulty": self.difficulty_label.text().replace("Difficulty: ", ""),
                    "category": self.category_combo.currentText(),
                    "date": datetime.now().isoformat()
                }
                
                # Load existing problems
                try:
                    with open("problems.json", "r") as f:
                        problems = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    problems = []
                
                # Add new problem if it doesn't exist
                if not any(p.get("title") == data["title"] for p in problems):
                    problems.append(data)
                
                # Save updated problems
                with open("problems.json", "w") as f:
                    json.dump(problems, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")

    def closeEvent(self, event):
        self.save_current_state()
        event.accept()

    def setup_reminder_timer(self):
        # Set up reminder timer
        self.reminder_timer = QTimer()
        self.reminder_timer.timeout.connect(self.check_reminder)
        self.reminder_timer.start(3600000)  # Check every hour

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    window = DSAProblemTracker()
    window.show()
    sys.exit(app.exec()) 