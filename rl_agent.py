import numpy as np
import pandas as pd
import pickle
import json
import re
import random
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
import hashlib

from logger import Logger
from device_actions import DeviceActions


class QLearningAgent:
    """Q-Learning based RL agent for device control with confidence scoring"""
    
    def __init__(self, 
                 learning_rate: float = 0.1,
                 discount_factor: float = 0.9,
                 epsilon: float = 0.2,
                 epsilon_decay: float = 0.995,
                 epsilon_min: float = 0.01,
                 qtable_file: str = "models/qtable.pkl"):
        
        # Q-learning parameters
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        
        # Q-table and experience storage
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.action_counts = defaultdict(lambda: defaultdict(int))
        self.state_visits = defaultdict(int)
        self.qtable_file = qtable_file
        
        # Components
        self.logger = Logger()
        self.device_actions = DeviceActions()
        self.available_actions = self.device_actions.get_available_actions()
        
        # Task and state management
        self.current_state = None
        self.current_task_id = None
        self.episode_rewards = []
        self.episode_actions = []
        self.episode_confidences = []
        
        # Intent parsing patterns
        self.intent_patterns = {
            "open_file": [r"open.*file", r"file.*browser", r"browse.*file", r"file.*manager", r"finder", r"explorer"],
            "open_notepad": [r"open.*notepad", r"text.*editor", r"edit.*text", r"create.*document", r"new.*text"],
            "mute_audio": [r"mute", r"silence", r"quiet", r"turn.*off.*audio", r"disable.*sound"],
            "unmute_audio": [r"unmute", r"sound.*on", r"audio.*on", r"enable.*sound", r"turn.*on.*audio"],
            "volume_up": [r"volume.*up", r"louder", r"increase.*volume", r"raise.*volume", r"boost.*sound"],
            "volume_down": [r"volume.*down", r"quieter", r"decrease.*volume", r"lower.*volume", r"reduce.*sound"],
            "take_screenshot": [r"screenshot", r"capture.*screen", r"screen.*shot", r"save.*screen", r"snap.*screen"],
            "open_browser": [r"open.*browser", r"web.*browser", r"internet", r"launch.*browser", r"start.*browser"],
            "open_calculator": [r"calculator", r"calc", r"math", r"arithmetic", r"compute"],
            "open_calendar": [r"calendar", r"schedule", r"appointments", r"events", r"planner"],
            "lock_screen": [r"lock.*screen", r"lock.*computer", r"secure.*system", r"screen.*lock"],
            "minimize_all_windows": [r"minimize.*all", r"hide.*all", r"desktop", r"show.*desktop", r"clear.*screen"],
            "close_active_window": [r"close.*window", r"close.*app", r"close.*current", r"exit.*window"],
            "open_task_manager": [r"task.*manager", r"activity.*monitor", r"processes", r"process.*manager"],
            "show_system_info": [r"system.*info", r"computer.*info", r"specs", r"hardware.*info", r"system.*specs"],
            "check_network_status": [r"network.*status", r"internet.*connection", r"connectivity", r"network.*test"],
            # New productivity patterns
            "open_notepad": [r"word.*document", r"text.*document", r"document.*editor", r"word.*processor"],
            "open_calculator": [r"spreadsheet", r"excel", r"numbers", r"calc.*sheet"],
            "open_browser": [r"search.*online", r"web.*search", r"google", r"browse.*web"],
            "open_calendar": [r"meeting", r"appointment", r"schedule.*meeting", r"calendar.*event"],
            # Media control patterns
            "take_screenshot": [r"record.*screen", r"screen.*recording", r"capture.*video"],
            "open_browser": [r"music.*player", r"media.*player", r"play.*music", r"audio.*player"],
            "show_system_info": [r"photo.*gallery", r"image.*viewer", r"picture.*viewer", r"photos"],
            # Security patterns
            "lock_screen": [r"privacy.*settings", r"security.*settings", r"enable.*firewall"],
            "show_system_info": [r"antivirus", r"malware.*scan", r"security.*scan"],
            "open_browser": [r"password.*manager", r"secure.*login", r"vpn.*connection"],
            # Development patterns
            "open_notepad": [r"code.*editor", r"ide", r"development.*environment", r"programming"],
            "open_terminal": [r"terminal", r"command.*prompt", r"console", r"shell", r"bash"],
            "show_system_info": [r"database.*client", r"server.*monitor", r"log.*viewer"],
            "open_task_manager": [r"docker", r"container", r"virtual.*machine", r"vm"]
        }
        
        # Load existing Q-table if available
        self.load_qtable()
        
        print(f"RL Agent initialized with {len(self.available_actions)} available actions")
        print(f"Q-table size: {len(self.q_table)} states")
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = random.randint(1000, 9999)
        return f"TASK_{timestamp}_{random_suffix}"
    
    def _parse_intent(self, task_description: str) -> str:
        """Parse natural language task into intent"""
        task_lower = task_description.lower().strip()
        
        # Direct action mapping
        if task_lower in self.available_actions:
            return task_lower
        
        # Pattern matching
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, task_lower):
                    return intent
        
        # Fallback: try to find closest action by keyword matching
        best_match = None
        best_score = 0
        
        for action in self.available_actions:
            # Calculate similarity score
            action_words = set(action.lower().replace('_', ' ').split())
            task_words = set(task_lower.replace('_', ' ').split())
            
            intersection = len(action_words.intersection(task_words))
            union = len(action_words.union(task_words))
            
            if union > 0:
                score = intersection / union
                if score > best_score and score > 0.3:  # Minimum threshold
                    best_score = score
                    best_match = action
        
        return best_match or "unknown_action"
    
    def _create_state_representation(self, task_intent: str, context: Dict = None) -> str:
        """Create state representation from task intent and context"""
        base_state = f"intent_{task_intent}"
        
        if context:
            # Add context information to state
            context_str = "_".join([f"{k}_{v}" for k, v in sorted(context.items()) 
                                  if isinstance(v, (str, int, bool))])
            if context_str:
                base_state += f"_ctx_{hashlib.md5(context_str.encode()).hexdigest()[:8]}"
        
        return base_state
    
    def _calculate_confidence_score(self, state: str, action: str) -> float:
        """Calculate confidence score for state-action pair"""
        if state not in self.q_table or not self.q_table[state]:
            return 0.0
        
        q_values = self.q_table[state]
        action_q = q_values.get(action, 0.0)
        
        if not q_values:
            return 0.0
        
        # Method 1: Normalized Q-value difference
        max_q = max(q_values.values())
        min_q = min(q_values.values())
        
        if max_q == min_q:
            confidence = 0.5  # Neutral confidence when all actions equal
        else:
            # Normalize the action's Q-value
            confidence = (action_q - min_q) / (max_q - min_q)
        
        # Method 2: Experience-based confidence boost
        action_count = self.action_counts[state].get(action, 0)
        experience_factor = min(action_count / 10.0, 1.0)  # Cap at 10 experiences
        
        # Combine both methods
        final_confidence = (confidence * 0.7) + (experience_factor * 0.3)
        
        return max(0.0, min(1.0, final_confidence))
    
    def _normalize_q_values(self, q_values: Dict[str, float]) -> Dict[str, float]:
        """Normalize Q-values to 0-1 range for better confidence interpretation"""
        if not q_values or len(q_values) < 2:
            return q_values
        
        q_vals = list(q_values.values())
        min_q = min(q_vals)
        max_q = max(q_vals)
        
        if max_q == min_q:
            # All Q-values are equal, normalize to 0.5
            return {action: 0.5 for action in q_values.keys()}
        
        # Normalize to 0-1 range
        normalized = {}
        for action, q_val in q_values.items():
            normalized[action] = (q_val - min_q) / (max_q - min_q)
        
        return normalized
    
    def _get_top_actions(self, state: str, n: int = 2) -> List[Tuple[str, float]]:
        """Get top N actions for a state with their Q-values"""
        if state not in self.q_table:
            # Return random actions if state not seen before
            random_actions = random.sample(self.available_actions, min(n, len(self.available_actions)))
            return [(action, 0.0) for action in random_actions]
        
        q_values = self.q_table[state]
        
        # Sort actions by Q-value
        sorted_actions = sorted(q_values.items(), key=lambda x: x[1], reverse=True)
        
        # Fill with unseen actions if needed
        seen_actions = set(q_values.keys())
        unseen_actions = [a for a in self.available_actions if a not in seen_actions]
        
        result = sorted_actions[:n]
        
        # Add unseen actions with Q-value 0 if we need more
        while len(result) < n and unseen_actions:
            action = unseen_actions.pop(0)
            result.append((action, 0.0))
        
        return result[:n]
    
    def select_action(self, state: str, task_intent: str = None) -> Tuple[str, float, List[Tuple[str, float]]]:
        """
        Select action using epsilon-greedy strategy with confidence scoring
        
        Returns:
            Tuple of (selected_action, confidence_score, next_best_actions)
        """
        # Get top actions for this state
        top_actions = self._get_top_actions(state, n=3)
        
        # Epsilon-greedy action selection
        if random.random() < self.epsilon:
            # Explore: choose random action
            selected_action = random.choice(self.available_actions)
        else:
            # Exploit: choose best action
            if top_actions:
                selected_action = top_actions[0][0]
            else:
                selected_action = random.choice(self.available_actions)
        
        # Calculate confidence for selected action
        confidence = self._calculate_confidence_score(state, selected_action)
        
        # Get next best actions (excluding the selected one)
        next_best = [action for action in top_actions if action[0] != selected_action][:2]
        
        # If we need more suggestions, add some from available actions
        if len(next_best) < 2:
            remaining_actions = [a for a in self.available_actions 
                               if a != selected_action and a not in [x[0] for x in next_best]]
            while len(next_best) < 2 and remaining_actions:
                action = remaining_actions.pop(0)
                next_best.append((action, self.q_table[state].get(action, 0.0)))
        
        return selected_action, confidence, next_best
    
    def execute_action(self, action: str) -> Tuple[bool, str, Dict, float]:
        """
        Execute an action and return results with internal reward
        
        Returns:
            Tuple of (success, message, info, internal_reward)
        """
        try:
            success, message, info = self.device_actions.execute_action(action)
            
            # Calculate internal reward based on success
            if success:
                internal_reward = 1.0
                # Bonus for successful actions that are complex
                if action in ["take_screenshot", "show_system_info", "check_network_status"]:
                    internal_reward = 1.5
            else:
                internal_reward = -1.0
                # Penalty for failed basic actions
                if action in ["open_file_browser", "open_notepad", "mute_audio"]:
                    internal_reward = -1.5
            
            return success, message, info, internal_reward
            
        except Exception as e:
            return False, f"Action execution error: {str(e)}", {}, -2.0
    
    def update_q_value(self, state: str, action: str, reward: float, next_state: str = None):
        """Update Q-value using Q-learning algorithm"""
        # Current Q-value
        current_q = self.q_table[state][action]
        
        # Future reward (for now, assume no next state - episodic tasks)
        if next_state and next_state in self.q_table and self.q_table[next_state]:
            max_future_q = max(self.q_table[next_state].values())
        else:
            max_future_q = 0.0
        
        # Q-learning update
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_future_q - current_q
        )
        
        # Update Q-table
        self.q_table[state][action] = new_q
        
        # Update action counts for confidence calculation
        self.action_counts[state][action] += 1
        self.state_visits[state] += 1
    
    def process_task(self, task_description: str, context: Dict = None) -> Dict[str, Any]:
        """
        Process a complete task from description to execution and learning
        
        Returns:
            Dictionary with task results and metrics
        """
        # Initialize task
        self.current_task_id = self._generate_task_id()
        parsed_intent = self._parse_intent(task_description)
        state = self._create_state_representation(parsed_intent, context)
        self.current_state = state
        
        print(f"\n🎯 Task {self.current_task_id}: '{task_description}'")
        print(f"📝 Parsed Intent: {parsed_intent}")
        print(f"🔍 State: {state}")
        
        # Select action
        selected_action, confidence, next_best_actions = self.select_action(state, parsed_intent)
        
        print(f"🤖 Selected Action: {selected_action} (Confidence: {confidence:.2f})")
        print(f"💡 Next Best Actions: {[f'{a}({q:.2f})' for a, q in next_best_actions]}")
        
        # Execute action
        success, message, info, internal_reward = self.execute_action(selected_action)
        
        print(f"⚡ Execution: {'✅ Success' if success else '❌ Failed'}")
        print(f"📋 Message: {message}")
        print(f"🎁 Internal Reward: {internal_reward}")
        
        # Log the action (before user feedback)
        self.logger.log_action(
            task_id=self.current_task_id,
            parsed_intent=parsed_intent,
            action_taken=selected_action,
            internal_reward=internal_reward,
            confidence_score=confidence,
            action_success=success,
            state_representation={"state": state, "context": context},
            q_values=dict(self.q_table[state]) if state in self.q_table else {},
            next_best_actions=[{"action": a, "q_value": q} for a, q in next_best_actions]
        )
        
        # Log detailed confidence information
        q_values_dict = dict(self.q_table[state]) if state in self.q_table else {}
        normalized_q_scores = self._normalize_q_values(q_values_dict)
        
        self.logger.log_confidence_per_task(
            task_id=self.current_task_id,
            task_description=task_description,
            confidence_score=confidence,
            state=state,
            action=selected_action,
            q_values=q_values_dict,
            normalized_scores=normalized_q_scores
        )
        
        # Store episode data
        self.episode_actions.append({
            "task_id": self.current_task_id,
            "state": state,
            "action": selected_action,
            "internal_reward": internal_reward,
            "confidence": confidence,
            "success": success
        })
        
        return {
            "task_id": self.current_task_id,
            "parsed_intent": parsed_intent,
            "selected_action": selected_action,
            "confidence_score": confidence,
            "next_best_actions": next_best_actions,
            "execution_success": success,
            "execution_message": message,
            "execution_info": info,
            "internal_reward": internal_reward,
            "state": state,
            "q_values": dict(self.q_table[state]) if state in self.q_table else {}
        }
    
    def receive_feedback(self, feedback: str, suggested_action: str = None) -> float:
        """
        Process user feedback and update learning
        
        Args:
            feedback: "👍", "👎", "positive", "negative"
            suggested_action: Action user suggests should have been taken
            
        Returns:
            Total reward for the last action
        """
        if not self.episode_actions:
            print("❌ No recent action to provide feedback for")
            return 0.0
        
        last_action_data = self.episode_actions[-1]
        state = last_action_data["state"]
        action = last_action_data["action"]
        internal_reward = last_action_data["internal_reward"]
        
        # Calculate feedback reward
        feedback_reward = 0.0
        if feedback in ["👍", "positive"]:
            feedback_reward = 0.5
            print(f"👍 Positive feedback received! (+{feedback_reward})")
        elif feedback in ["👎", "negative"]:
            feedback_reward = -0.5
            print(f"👎 Negative feedback received! ({feedback_reward})")
        
        total_reward = internal_reward + feedback_reward
        
        # Update Q-value with total reward
        self.update_q_value(state, action, total_reward)
        
        # If negative feedback and suggestion provided, boost suggested action
        if feedback in ["👎", "negative"] and suggested_action:
            if suggested_action in self.available_actions:
                # Give the suggested action a positive boost
                self.update_q_value(state, suggested_action, 1.0)
                print(f"💡 Boosted suggested action: {suggested_action}")
            else:
                print(f"⚠️ Suggested action '{suggested_action}' not recognized")
        
        # Update logs with feedback
        self.logger.log_action(
            task_id=last_action_data["task_id"],
            parsed_intent="feedback_update",
            action_taken=f"feedback_{feedback}",
            internal_reward=0.0,
            confidence_score=last_action_data["confidence"],
            user_feedback=feedback,
            suggested_correct_action=suggested_action,
            state_representation={"feedback_for_state": state},
            q_values=dict(self.q_table[state])
        )
        
        # Update feedback summary
        self.logger.update_feedback_summary(feedback)
        
        # Store episode reward
        self.episode_rewards.append(total_reward)
        self.episode_confidences.append(last_action_data["confidence"])
        
        # Decay epsilon (reduce exploration over time)
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        print(f"🎯 Total Reward: {total_reward:.2f}")
        print(f"📊 Q-value updated for state '{state}', action '{action}'")
        print(f"🔍 Exploration rate: {self.epsilon:.3f}")
        
        return total_reward
    
    def end_episode(self):
        """End current episode and log metrics"""
        if not self.episode_rewards:
            return
        
        total_reward = sum(self.episode_rewards)
        avg_confidence = np.mean(self.episode_confidences) if self.episode_confidences else 0.0
        success_rate = np.mean([a["success"] for a in self.episode_actions]) if self.episode_actions else 0.0
        
        # Log episode metrics
        self.logger.log_episode_metrics(
            total_reward=total_reward,
            average_confidence=avg_confidence,
            success_rate=success_rate,
            exploration_rate=self.epsilon
        )
        
        print(f"\n📊 Episode Complete:")
        print(f"   Total Reward: {total_reward:.2f}")
        print(f"   Average Confidence: {avg_confidence:.2f}")
        print(f"   Success Rate: {success_rate:.2f}")
        print(f"   Actions Taken: {len(self.episode_actions)}")
        
        # Reset episode data
        self.episode_rewards = []
        self.episode_actions = []
        self.episode_confidences = []
        
        # Save Q-table after episode
        self.save_qtable()
    
    def save_qtable(self):
        """Save Q-table to both pickle and CSV files"""
        try:
            os.makedirs(os.path.dirname(self.qtable_file), exist_ok=True)
            
            qtable_data = {
                "q_table": dict(self.q_table),
                "action_counts": dict(self.action_counts),
                "state_visits": dict(self.state_visits),
                "epsilon": self.epsilon,
                "metadata": {
                    "total_states": len(self.q_table),
                    "total_actions": len(self.available_actions),
                    "last_saved": datetime.now().isoformat()
                }
            }
            
            # Save to pickle (existing functionality)
            with open(self.qtable_file, 'wb') as f:
                pickle.dump(qtable_data, f)
            
            # Save to CSV for review
            self.save_qtable_csv()
            
            print(f"💾 Q-table saved to {self.qtable_file} and CSV")
            
        except Exception as e:
            print(f"❌ Failed to save Q-table: {e}")
    
    def load_qtable(self):
        """Load Q-table from file (pickle preferred, CSV fallback)"""
        try:
            if os.path.exists(self.qtable_file):
                with open(self.qtable_file, 'rb') as f:
                    qtable_data = pickle.load(f)
                
                self.q_table = defaultdict(lambda: defaultdict(float), qtable_data.get("q_table", {}))
                self.action_counts = defaultdict(lambda: defaultdict(int), qtable_data.get("action_counts", {}))
                self.state_visits = defaultdict(int, qtable_data.get("state_visits", {}))
                self.epsilon = qtable_data.get("epsilon", self.epsilon)
                
                metadata = qtable_data.get("metadata", {})
                print(f"📚 Q-table loaded from {self.qtable_file}")
                print(f"   States: {metadata.get('total_states', len(self.q_table))}")
                print(f"   Last saved: {metadata.get('last_saved', 'Unknown')}")
                
            else:
                print(f"📝 No existing Q-table found, trying CSV fallback")
                self.load_qtable_csv()
                
        except Exception as e:
            print(f"❌ Failed to load Q-table from pickle: {e}")
            print(f"📝 Trying CSV fallback")
            self.load_qtable_csv()
    
    def save_qtable_csv(self):
        """Save Q-table to CSV format for review and analysis"""
        try:
            # Create CSV filename
            csv_file = self.qtable_file.replace('.pkl', '.csv')
            
            # Prepare data for CSV export
            csv_data = []
            
            for state, actions in self.q_table.items():
                for action, q_value in actions.items():
                    csv_data.append({
                        'state': state,
                        'action': action,
                        'q_value': q_value,
                        'action_count': self.action_counts[state].get(action, 0),
                        'state_visits': self.state_visits.get(state, 0),
                        'last_updated': datetime.now().isoformat()
                    })
            
            # Create DataFrame and save to CSV
            df = pd.DataFrame(csv_data)
            df.to_csv(csv_file, index=False)
            
            # Save metadata separately
            metadata_file = csv_file.replace('.csv', '_metadata.json')
            metadata = {
                'epsilon': self.epsilon,
                'total_states': len(self.q_table),
                'total_actions': len(self.available_actions),
                'available_actions': self.available_actions,
                'export_timestamp': datetime.now().isoformat(),
                'learning_parameters': {
                    'learning_rate': self.learning_rate,
                    'discount_factor': self.discount_factor,
                    'epsilon_decay': self.epsilon_decay,
                    'epsilon_min': self.epsilon_min
                }
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"📊 Q-table exported to CSV: {csv_file}")
            print(f"📊 Metadata saved to: {metadata_file}")
            
        except Exception as e:
            print(f"❌ Failed to save Q-table to CSV: {e}")
    
    def load_qtable_csv(self):
        """Load Q-table from CSV format"""
        try:
            csv_file = self.qtable_file.replace('.pkl', '.csv')
            metadata_file = csv_file.replace('.csv', '_metadata.json')
            
            if not os.path.exists(csv_file):
                print(f"📝 No CSV Q-table found, starting fresh")
                return
            
            # Load Q-table data
            df = pd.read_csv(csv_file)
            
            # Reconstruct Q-table
            self.q_table = defaultdict(lambda: defaultdict(float))
            self.action_counts = defaultdict(lambda: defaultdict(int))
            self.state_visits = defaultdict(int)
            
            for _, row in df.iterrows():
                state = row['state']
                action = row['action']
                q_value = row['q_value']
                action_count = row['action_count']
                state_visits = row['state_visits']
                
                self.q_table[state][action] = q_value
                self.action_counts[state][action] = action_count
                self.state_visits[state] = state_visits
            
            # Load metadata if available
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    self.epsilon = metadata.get('epsilon', self.epsilon)
                    
                print(f"📚 Q-table loaded from CSV: {csv_file}")
                print(f"   States: {len(self.q_table)}")
                print(f"   Export timestamp: {metadata.get('export_timestamp', 'Unknown')}")
            else:
                print(f"📚 Q-table loaded from CSV: {csv_file} (no metadata)")
                
        except Exception as e:
            print(f"❌ Failed to load Q-table from CSV: {e}")
            print(f"📝 Starting with empty Q-table")
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get comprehensive learning statistics"""
        stats = {
            "qtable_stats": {
                "total_states": len(self.q_table),
                "total_state_action_pairs": sum(len(actions) for actions in self.q_table.values()),
                "most_visited_states": sorted(self.state_visits.items(), key=lambda x: x[1], reverse=True)[:5],
                "exploration_rate": self.epsilon
            },
            "session_stats": self.logger.get_session_summary(),
            "learning_history": self.logger.get_learning_history().to_dict('records') if not self.logger.get_learning_history().empty else []
        }
        
        return stats
    
    def suggest_next_actions(self, current_context: str = None) -> List[Tuple[str, float, str]]:
        """
        Suggest next actions based on current context
        
        Returns:
            List of (action, confidence, reasoning)
        """
        if current_context:
            state = self._create_state_representation(self._parse_intent(current_context))
        else:
            # Use most common state if no context
            if self.state_visits:
                state = max(self.state_visits.items(), key=lambda x: x[1])[0]
            else:
                return [("take_screenshot", 0.5, "Good starting action"), 
                       ("show_system_info", 0.5, "Learn about system")]
        
        top_actions = self._get_top_actions(state, n=3)
        
        suggestions = []
        for action, q_value in top_actions:
            confidence = self._calculate_confidence_score(state, action)
            reasoning = f"Q-value: {q_value:.2f}, visited {self.action_counts[state].get(action, 0)} times"
            suggestions.append((action, confidence, reasoning))
        
        return suggestions


def main():
    """Main CLI interface for the RL agent"""
    print("🤖 RL Device Agent v2 - Command Line Interface")
    print("=" * 50)
    
    agent = QLearningAgent()
    
    print("\nCommands:")
    print("  - Type a task description (e.g., 'open notepad', 'mute audio')")
    print("  - After action execution, provide feedback: 👍 or 👎")
    print("  - Type 'stats' to see learning statistics")
    print("  - Type 'suggest' to get action suggestions")
    print("  - Type 'quit' to exit")
    print("=" * 50)
    
    try:
        while True:
            user_input = input("\n🎯 Enter task or command: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            elif user_input.lower() == 'stats':
                stats = agent.get_learning_statistics()
                print("\n📊 Learning Statistics:")
                print(f"States learned: {stats['qtable_stats']['total_states']}")
                print(f"State-action pairs: {stats['qtable_stats']['total_state_action_pairs']}")
                print(f"Exploration rate: {stats['qtable_stats']['exploration_rate']:.3f}")
                print(f"Session actions: {stats['session_stats']['total_actions']}")
                print(f"Average reward: {stats['session_stats']['average_reward']:.2f}")
                continue
            
            elif user_input.lower() == 'suggest':
                suggestions = agent.suggest_next_actions()
                print("\n💡 Suggested Actions:")
                for i, (action, conf, reason) in enumerate(suggestions, 1):
                    print(f"{i}. {action} (confidence: {conf:.2f}) - {reason}")
                continue
            
            elif user_input in ['👍', '👎', 'positive', 'negative']:
                # Process feedback
                if agent.episode_actions:
                    suggested_action = None
                    if user_input in ['👎', 'negative']:
                        suggested = input("What action should have been taken? (optional): ").strip()
                        if suggested:
                            suggested_action = suggested
                    
                    agent.receive_feedback(user_input, suggested_action)
                else:
                    print("❌ No recent action to provide feedback for")
                continue
            
            elif user_input:
                # Process task
                result = agent.process_task(user_input)
                
                # Ask for feedback
                print(f"\n💬 How was this action? (👍/👎 or type feedback)")
                
            else:
                print("❌ Please enter a valid task or command")
    
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
    
    finally:
        # End episode and save
        agent.end_episode()
        print("📊 Learning session completed!")


if __name__ == "__main__":
    main()