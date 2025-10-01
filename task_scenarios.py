"""
Task Scenarios Generator and Demo Script for RL Device Agent v2

This module provides diverse task scenarios and automated demo functionality
to showcase the agent's learning capabilities and user interaction features.
"""

import random
import time
import json
from datetime import datetime
from typing import List, Dict, Tuple, Union
import numpy as np

from rl_agent import QLearningAgent
from logger import Logger
from visualizer import LearningVisualizer


class TaskScenarios:
    """Generate diverse task scenarios for training and demo"""
    
    def __init__(self):
        self.task_categories = {
            "file_operations": [
                "open file browser",
                "open notepad",
                "open text editor", 
                "create new file",
                "browse files",
                "open file manager",
                "edit text file",
                "start text editor",
                "create document",
                "new text document",
                "open documents folder",
                "access downloads",
                "show desktop files",
                "open pictures folder",
                "browse documents",
                "file explorer",
                "finder window",
                "create folder",
                "make new directory"
            ],
            "audio_control": [
                "mute audio",
                "unmute audio",
                "mute sound",
                "turn off audio",
                "silence computer",
                "turn on sound",
                "toggle audio",
                "volume up",
                "volume down",
                "increase volume",
                "decrease volume",
                "make it louder",
                "make it quieter",
                "adjust sound",
                "control volume",
                "max volume",
                "minimum volume",
                "sound settings",
                "audio preferences",
                "speaker volume",
                "microphone mute"
            ],
            "system_operations": [
                "take screenshot",
                "capture screen",
                "screen shot",
                "save screen image",
                "lock screen",
                "lock computer",
                "secure system",
                "show system info",
                "system information",
                "computer specs",
                "check network",
                "network status",
                "internet connection",
                "connectivity test",
                "disk usage",
                "memory usage",
                "cpu usage",
                "battery status",
                "power settings",
                "display settings",
                "screen resolution",
                "system performance",
                "hardware info",
                "storage space",
                "check updates"
            ],
            "application_control": [
                "open browser",
                "start web browser",
                "open internet",
                "launch browser",
                "open calculator",
                "start calculator",
                "math calculator",
                "open calendar",
                "show calendar",
                "calendar app",
                "schedule application",
                "open terminal",
                "command prompt",
                "start terminal",
                "open settings",
                "system settings",
                "preferences",
                "control panel",
                "launch email",
                "open mail app",
                "start music player",
                "photo viewer",
                "image editor",
                "video player",
                "code editor",
                "word processor",
                "spreadsheet app",
                "presentation software",
                "file archiver",
                "zip utility",
                "antivirus software",
                "backup utility"
            ],
            "window_management": [
                "minimize all windows",
                "hide all windows",
                "show desktop",
                "minimize everything",
                "close active window",
                "close current window",
                "close this window",
                "maximize window",
                "make window bigger",
                "minimize window",
                "make window smaller",
                "switch window",
                "change window",
                "alt tab",
                "close all windows",
                "close everything",
                "tile windows",
                "arrange windows",
                "split screen",
                "snap window left",
                "snap window right",
                "fullscreen mode",
                "window on top",
                "bring to front",
                "send to back",
                "restore window",
                "move window",
                "resize window"
            ],
            "task_management": [
                "open task manager",
                "activity monitor",
                "process manager",
                "show running programs",
                "task list",
                "system monitor",
                "show processes",
                "running applications",
                "performance monitor",
                "resource monitor",
                "cpu monitor",
                "memory monitor",
                "disk monitor",
                "network monitor",
                "process viewer",
                "kill process",
                "end task",
                "force quit",
                "startup programs",
                "background processes"
            ],
            "productivity_tasks": [
                "open word document",
                "create presentation",
                "new spreadsheet",
                "open pdf reader",
                "start video call",
                "send email",
                "check messages",
                "open chat app",
                "schedule meeting",
                "set reminder",
                "create note",
                "open notebook",
                "start timer",
                "stopwatch",
                "alarm clock",
                "weather app",
                "news reader",
                "search online",
                "translate text",
                "dictionary lookup"
            ],
            "media_content": [
                "play music",
                "pause music",
                "next song",
                "previous track",
                "open playlist",
                "video player",
                "watch video",
                "photo gallery",
                "slideshow",
                "image viewer",
                "edit photo",
                "crop image",
                "resize photo",
                "media library",
                "podcast player",
                "audiobook player",
                "radio app",
                "streaming service",
                "record audio",
                "screen recording"
            ],
            "security_privacy": [
                "enable firewall",
                "check antivirus",
                "scan for malware",
                "update security",
                "privacy settings",
                "clear browser data",
                "delete cookies",
                "clear cache",
                "password manager",
                "secure login",
                "two factor auth",
                "vpn connection",
                "private browsing",
                "incognito mode",
                "encrypt files",
                "secure delete",
                "backup data",
                "restore backup",
                "permission settings",
                "access control"
            ],
            "development_tools": [
                "open code editor",
                "start ide",
                "compile code",
                "run debugger",
                "version control",
                "git repository",
                "database client",
                "api testing",
                "server monitor",
                "log viewer",
                "terminal emulator",
                "ssh client",
                "ftp client",
                "docker container",
                "virtual machine",
                "package manager",
                "dependency installer",
                "build automation",
                "test runner",
                "code formatter"
            ]
        }
        
        # Create flat list of all tasks
        self.all_tasks = []
        for category, tasks in self.task_categories.items():
            for task in tasks:
                self.all_tasks.append({
                    "description": task,
                    "category": category,
                    "difficulty": self._assess_difficulty(task, category)
                })
    
    def _assess_difficulty(self, task: str, category: str) -> str:
        """Assess task difficulty based on category and complexity"""
        difficulty_map = {
            "file_operations": "easy",
            "audio_control": "easy", 
            "application_control": "medium",
            "system_operations": "medium",
            "window_management": "medium",
            "task_management": "hard",
            "productivity_tasks": "medium",
            "media_content": "easy",
            "security_privacy": "hard",
            "development_tools": "hard"
        }
        
        # Adjust based on task specificity
        if any(word in task.lower() for word in ["all", "everything", "multiple"]):
            return "hard"
        elif any(word in task.lower() for word in ["info", "status", "check", "show"]):
            return "medium"
        
        return difficulty_map.get(category, "medium")
    
    def get_random_task(self, category: str | None = None, difficulty: str | None = None) -> Dict:
        """Get a random task, optionally filtered by category or difficulty"""
        available_tasks = self.all_tasks.copy()
        
        if category:
            available_tasks = [t for t in available_tasks if t["category"] == category]
        
        if difficulty:
            available_tasks = [t for t in available_tasks if t["difficulty"] == difficulty]
        
        if not available_tasks:
            available_tasks = self.all_tasks
        
        return random.choice(available_tasks)
    
    def get_task_sequence(self, count: int = 15, balanced: bool = True) -> List[Dict]:
        """Get a sequence of diverse tasks"""
        if balanced:
            # Ensure representation from each category
            tasks = []
            categories = list(self.task_categories.keys())
            
            # Distribute tasks across categories
            tasks_per_category = count // len(categories)
            remainder = count % len(categories)
            
            for i, category in enumerate(categories):
                category_count = tasks_per_category + (1 if i < remainder else 0)
                category_tasks = [t for t in self.all_tasks if t["category"] == category]
                
                # Randomly select tasks from this category
                selected = random.sample(category_tasks, min(category_count, len(category_tasks)))
                tasks.extend(selected)
            
            # Shuffle the final sequence
            random.shuffle(tasks)
        else:
            # Completely random selection
            tasks = random.sample(self.all_tasks, min(count, len(self.all_tasks)))
        
        return tasks
    
    def save_task_log(self, tasks: List[Dict], filename: str = "logs/task_log.txt"):
        """Save task sequence to log file"""
        with open(filename, 'w') as f:
            f.write("RL Device Agent v2 - Task Log\n")
            f.write("=" * 40 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Tasks: {len(tasks)}\n\n")
            
            # Summary by category
            category_counts = {}
            for task in tasks:
                category = task["category"]
                category_counts[category] = category_counts.get(category, 0) + 1
            
            f.write("Tasks by Category:\n")
            for category, count in category_counts.items():
                f.write(f"  {category}: {count}\n")
            f.write("\n")
            
            # Task list
            f.write("Task Sequence:\n")
            f.write("-" * 40 + "\n")
            for i, task in enumerate(tasks, 1):
                f.write(f"{i:2d}. [{task['category']}] {task['description']} "
                       f"(difficulty: {task['difficulty']})\n")
        
        print(f"📝 Task log saved to: {filename}")


class DemoRunner:
    """Automated demo runner for showcasing agent capabilities"""
    
    def __init__(self, agent: QLearningAgent | None = None, interactive: bool = True):
        self.agent = agent or QLearningAgent()
        self.interactive = interactive
        self.task_scenarios = TaskScenarios()
        self.demo_results = []
        
    def run_demo_sequence(self, num_tasks: int = 15, feedback_probability: float = 0.8):
        """Run a demonstration sequence with automated feedback"""
        print("🎬 Starting RL Device Agent v2 Demo")
        print("=" * 50)
        
        # Generate task sequence
        tasks = self.task_scenarios.get_task_sequence(num_tasks, balanced=True)
        self.task_scenarios.save_task_log(tasks)
        
        demo_start_time = datetime.now()
        
        for i, task_info in enumerate(tasks, 1):
            print(f"\n🎯 Demo Task {i}/{num_tasks}")
            print("-" * 30)
            
            # Execute task
            task_description = task_info["description"]
            result = self.agent.process_task(task_description)
            
            # Store demo result
            demo_result = {
                "task_number": i,
                "task_info": task_info,
                "execution_result": result,
                "timestamp": datetime.now()
            }
            
            # Automated or interactive feedback
            if random.random() < feedback_probability:
                if self.interactive:
                    feedback, suggestion = self._get_interactive_feedback()
                else:
                    feedback, suggestion = self._get_automated_feedback(result, task_info)
                
                if feedback:
                    reward = self.agent.receive_feedback(feedback, suggestion or "")
                    demo_result["feedback"] = feedback
                    demo_result["suggestion"] = suggestion
                    demo_result["final_reward"] = reward
            
            self.demo_results.append(demo_result)
            
            # Short pause between tasks
            if self.interactive:
                input("\nPress Enter to continue to next task...")
            else:
                time.sleep(1)
        
        # End episode and generate report
        self.agent.end_episode()
        
        demo_end_time = datetime.now()
        demo_duration = demo_end_time - demo_start_time
        
        print(f"\n🎉 Demo Complete!")
        print(f"Duration: {demo_duration}")
        print(f"Tasks completed: {len(tasks)}")
        
        # Generate demo report
        self._generate_demo_report(demo_start_time, demo_end_time)
        
        return self.demo_results
    
    def _get_interactive_feedback(self) -> Tuple[str | None, str | None]:
        """Get feedback interactively from user"""
        print("\n💬 Provide feedback for this action:")
        print("Options: 👍 (good), 👎 (wrong), skip")
        
        while True:
            feedback_input = input("Your feedback: ").strip().lower()
            
            if feedback_input in ['👍', 'good', 'positive', 'yes', 'y']:
                return "👍", None
            elif feedback_input in ['👎', 'bad', 'wrong', 'negative', 'no', 'n']:
                suggestion = input("What should have been done? (optional): ").strip()
                return "👎", suggestion if suggestion else None
            elif feedback_input in ['skip', 's', '']:
                return None, None
            else:
                print("Invalid input. Use 👍, 👎, or skip")
    
    def _get_automated_feedback(self, result: Dict, task_info: Dict) -> Tuple[str | None, str | None]:
        """Generate automated feedback based on execution success and context"""
        execution_success = result.get("execution_success", False)
        confidence_score = result.get("confidence_score", 0.0)
        
        # Basic feedback logic
        if execution_success and confidence_score > 0.7:
            # High confidence successful action - likely correct
            return "👍", None
        elif execution_success and confidence_score > 0.4:
            # Medium confidence - random feedback to create learning variety
            return random.choice(["👍", "👎"]), None
        elif not execution_success:
            # Failed execution - negative feedback with suggestion
            category = task_info.get("category", "")
            
            # Suggest alternative action based on category
            suggestions = {
                "file_operations": "open_file_browser",
                "audio_control": "mute_audio",
                "system_operations": "take_screenshot",
                "application_control": "open_browser",
                "window_management": "minimize_all_windows",
                "task_management": "open_task_manager"
            }
            
            suggested_action = suggestions.get(category, "take_screenshot")
            return "👎", suggested_action
        else:
            # Low confidence - provide some feedback for learning
            return random.choice(["👍", "👎"]), None
    
    def _generate_demo_report(self, start_time: datetime, end_time: datetime):
        """Generate comprehensive demo report"""
        # Calculate statistics
        total_tasks = len(self.demo_results)
        successful_tasks = sum(1 for r in self.demo_results if r["execution_result"]["execution_success"])
        tasks_with_feedback = sum(1 for r in self.demo_results if "feedback" in r)
        positive_feedback = sum(1 for r in self.demo_results if r.get("feedback") == "👍")
        
        # Generate visualizations
        visualizer = LearningVisualizer(self.agent.logger)
        plots = visualizer.create_comprehensive_report()
        
        # Create text report
        report_content = f"""
RL Device Agent v2 - Demo Report
================================

Demo Session Information:
- Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}
- End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
- Duration: {end_time - start_time}

Task Execution Summary:
- Total Tasks: {total_tasks}
- Successful Executions: {successful_tasks} ({successful_tasks/total_tasks:.1%})
- Tasks with Feedback: {tasks_with_feedback} ({tasks_with_feedback/total_tasks:.1%})
- Positive Feedback: {positive_feedback} ({positive_feedback/tasks_with_feedback:.1%} of feedback)

Learning Statistics:
- Final Q-table Size: {len(self.agent.q_table)} states
- Exploration Rate: {self.agent.epsilon:.3f}
- Session Summary: {self.agent.logger.get_session_summary()}

Task Categories Covered:
"""
        
        # Add category breakdown
        category_counts = {}
        for result in self.demo_results:
            category = result["task_info"]["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
        
        for category, count in category_counts.items():
            report_content += f"- {category}: {count} tasks\n"
        
        report_content += f"""

Detailed Task Results:
"""
        
        for result in self.demo_results:
            task_num = result["task_number"]
            task_desc = result["task_info"]["description"]
            success = "✅" if result["execution_result"]["execution_success"] else "❌"
            confidence = result["execution_result"]["confidence_score"]
            feedback = result.get("feedback", "No feedback")
            
            report_content += f"{task_num:2d}. {success} {task_desc} (confidence: {confidence:.2f}, feedback: {feedback})\n"
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"logs/demo_report_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write(report_content)
        
        print(f"📊 Demo report saved to: {report_file}")
        
        return report_file
    
    def run_interactive_demo(self):
        """Run interactive demo with user participation"""
        print("🎬 Interactive RL Device Agent v2 Demo")
        print("=" * 50)
        print("In this demo, you'll see the agent process tasks and provide feedback.")
        print("Your feedback helps the agent learn and improve its performance.")
        
        input("\nPress Enter to start the interactive demo...")
        
        return self.run_demo_sequence(num_tasks=10, feedback_probability=1.0)
    
    def run_automated_demo(self, num_tasks: int = 15):
        """Run automated demo for development/testing"""
        print("🤖 Automated RL Device Agent v2 Demo")
        print("=" * 50)
        print("Running automated demo with simulated user feedback...")
        
        return self.run_demo_sequence(num_tasks=num_tasks, feedback_probability=0.8)


def create_sample_task_log():
    """Create a sample task log with diverse scenarios"""
    scenarios = TaskScenarios()
    tasks = scenarios.get_task_sequence(15, balanced=True)
    scenarios.save_task_log(tasks, "logs/task_log.txt")
    
    print("✅ Sample task log created with 15 diverse tasks")
    return tasks


def main():
    """Main function for running demos and generating scenarios"""
    print("🤖 RL Device Agent v2 - Task Scenarios & Demo")
    print("=" * 50)
    
    while True:
        print("\nSelect an option:")
        print("1. Run Interactive Demo")
        print("2. Run Automated Demo") 
        print("3. Generate Task Scenarios")
        print("4. Create Sample Task Log")
        print("5. Quick Learning Demo (5 tasks)")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            agent = QLearningAgent()
            demo_runner = DemoRunner(agent, interactive=True)
            demo_runner.run_interactive_demo()
            
        elif choice == "2":
            agent = QLearningAgent()
            demo_runner = DemoRunner(agent, interactive=False)
            demo_runner.run_automated_demo(15)
            
        elif choice == "3":
            scenarios = TaskScenarios()
            tasks = scenarios.get_task_sequence(20, balanced=True)
            print(f"\n📝 Generated {len(tasks)} diverse tasks:")
            for i, task in enumerate(tasks[:10], 1):
                print(f"{i:2d}. [{task['category']}] {task['description']}")
            if len(tasks) > 10:
                print(f"... and {len(tasks)-10} more tasks")
            
        elif choice == "4":
            create_sample_task_log()
            
        elif choice == "5":
            agent = QLearningAgent()
            demo_runner = DemoRunner(agent, interactive=False)
            demo_runner.run_automated_demo(5)
            
        elif choice == "6":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-6.")


if __name__ == "__main__":
    main()