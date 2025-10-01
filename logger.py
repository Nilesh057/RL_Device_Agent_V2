import csv
import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional, List
import pandas as pd


class Logger:
    """Comprehensive logging system for RL Device Agent"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self.action_log_file = os.path.join(log_dir, "action_log.csv")
        self.task_log_file = os.path.join(log_dir, "task_log.txt")
        self.db_file = os.path.join(log_dir, "agent_data.db")
        
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Initialize CSV log file with headers
        self._init_csv_log()
        
        # Initialize SQLite database
        self._init_database()
        
        # Session tracking
        self.current_session_id = self._generate_session_id()
        self.episode_count = 0
        
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _init_csv_log(self):
        """Initialize CSV log file with headers"""
        headers = [
            "timestamp", "session_id", "episode", "task_id", "parsed_intent",
            "action_taken", "internal_reward", "user_feedback", "total_reward",
            "confidence_score", "suggested_correct_action", "action_success",
            "state_representation", "q_values", "next_best_actions"
        ]
        
        # Create file with headers if it doesn't exist
        if not os.path.exists(self.action_log_file):
            with open(self.action_log_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
    
    def _init_database(self):
        """Initialize SQLite database for structured logging"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL,
                episode INTEGER,
                task_id TEXT,
                parsed_intent TEXT,
                action_taken TEXT,
                internal_reward REAL,
                user_feedback TEXT,
                total_reward REAL,
                confidence_score REAL,
                suggested_correct_action TEXT,
                action_success BOOLEAN,
                state_representation TEXT,
                q_values TEXT,
                next_best_actions TEXT
            )
        ''')
        
        # Create learning_metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                episode INTEGER,
                total_reward REAL,
                average_confidence REAL,
                success_rate REAL,
                exploration_rate REAL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        # Create feedback_summary table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                total_positive INTEGER DEFAULT 0,
                total_negative INTEGER DEFAULT 0,
                total_actions INTEGER DEFAULT 0,
                last_updated TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_action(self, 
                   task_id: str,
                   parsed_intent: str,
                   action_taken: str,
                   internal_reward: float,
                   confidence_score: float,
                   user_feedback: Optional[str] = None,
                   suggested_correct_action: Optional[str] = None,
                   action_success: bool = True,
                   state_representation: Optional[Dict] = None,
                   q_values: Optional[Dict] = None,
                   next_best_actions: Optional[List] = None) -> None:
        """Log a single action with all required fields"""
        
        timestamp = datetime.now().isoformat()
        
        # Calculate total reward
        feedback_reward = 0.0
        if user_feedback == "👍" or user_feedback == "positive":
            feedback_reward = 0.5
        elif user_feedback == "👎" or user_feedback == "negative":
            feedback_reward = -0.5
        
        total_reward = internal_reward + feedback_reward
        
        # Prepare data for logging
        log_data = {
            "timestamp": timestamp,
            "session_id": self.current_session_id,
            "episode": self.episode_count,
            "task_id": task_id,
            "parsed_intent": parsed_intent,
            "action_taken": action_taken,
            "internal_reward": internal_reward,
            "user_feedback": user_feedback or "",
            "total_reward": total_reward,
            "confidence_score": confidence_score,
            "suggested_correct_action": suggested_correct_action or "",
            "action_success": action_success,
            "state_representation": json.dumps(state_representation) if state_representation else "",
            "q_values": json.dumps(q_values) if q_values else "",
            "next_best_actions": json.dumps(next_best_actions) if next_best_actions else ""
        }
        
        # Log to CSV
        self._log_to_csv(log_data)
        
        # Log to SQLite
        self._log_to_database(log_data)
        
        # Log to task log file
        self._log_to_task_file(task_id, parsed_intent, action_taken, total_reward)
        
        print(f"✓ Logged action: {action_taken} (Reward: {total_reward:.2f}, Confidence: {confidence_score:.2f})")
    
    def _log_to_csv(self, data: Dict[str, Any]):
        """Log data to CSV file"""
        with open(self.action_log_file, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data.keys())
            writer.writerow(data)
    
    def _log_to_database(self, data: Dict[str, Any]):
        """Log data to SQLite database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO actions (
                timestamp, session_id, episode, task_id, parsed_intent,
                action_taken, internal_reward, user_feedback, total_reward,
                confidence_score, suggested_correct_action, action_success,
                state_representation, q_values, next_best_actions
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data["timestamp"], data["session_id"], data["episode"],
            data["task_id"], data["parsed_intent"], data["action_taken"],
            data["internal_reward"], data["user_feedback"], data["total_reward"],
            data["confidence_score"], data["suggested_correct_action"],
            data["action_success"], data["state_representation"],
            data["q_values"], data["next_best_actions"]
        ))
        
        conn.commit()
        conn.close()
    
    def _log_to_task_file(self, task_id: str, intent: str, action: str, reward: float):
        """Log to human-readable task file"""
        with open(self.task_log_file, 'a') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] Task: {task_id} | Intent: {intent} | Action: {action} | Reward: {reward:.2f}\n")
    
    def log_episode_metrics(self, total_reward: float, average_confidence: float, 
                           success_rate: float, exploration_rate: float):
        """Log episode-level metrics"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO learning_metrics (
                session_id, episode, total_reward, average_confidence,
                success_rate, exploration_rate, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.current_session_id, self.episode_count, total_reward,
            average_confidence, success_rate, exploration_rate,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        self.episode_count += 1
    
    def update_feedback_summary(self, feedback_type: str):
        """Update feedback summary statistics"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Get or create feedback summary for current session
        cursor.execute('''
            SELECT total_positive, total_negative, total_actions 
            FROM feedback_summary 
            WHERE session_id = ?
        ''', (self.current_session_id,))
        
        result = cursor.fetchone()
        
        if result:
            total_positive, total_negative, total_actions = result
        else:
            total_positive, total_negative, total_actions = 0, 0, 0
        
        # Update counts
        total_actions += 1
        if feedback_type in ["👍", "positive"]:
            total_positive += 1
        elif feedback_type in ["👎", "negative"]:
            total_negative += 1
        
        # Insert or update
        cursor.execute('''
            INSERT OR REPLACE INTO feedback_summary (
                session_id, total_positive, total_negative, total_actions, last_updated
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            self.current_session_id, total_positive, total_negative,
            total_actions, datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_learning_history(self) -> pd.DataFrame:
        """Get learning history for visualization"""
        conn = sqlite3.connect(self.db_file)
        df = pd.read_sql_query('''
            SELECT episode, total_reward, average_confidence, success_rate
            FROM learning_metrics
            ORDER BY episode
        ''', conn)
        conn.close()
        return df
    
    def get_action_history(self, limit: int = 100) -> pd.DataFrame:
        """Get recent action history"""
        conn = sqlite3.connect(self.db_file)
        df = pd.read_sql_query('''
            SELECT timestamp, task_id, parsed_intent, action_taken,
                   total_reward, confidence_score, user_feedback
            FROM actions
            ORDER BY timestamp DESC
            LIMIT ?
        ''', conn, params=[limit])
        conn.close()
        return df
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary statistics for current session"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Get action statistics
        cursor.execute('''
            SELECT COUNT(*) as total_actions,
                   AVG(total_reward) as avg_reward,
                   AVG(confidence_score) as avg_confidence,
                   SUM(CASE WHEN action_success = 1 THEN 1 ELSE 0 END) as successful_actions
            FROM actions
            WHERE session_id = ?
        ''', (self.current_session_id,))
        
        action_stats = cursor.fetchone()
        
        # Get feedback statistics
        cursor.execute('''
            SELECT total_positive, total_negative, total_actions
            FROM feedback_summary
            WHERE session_id = ?
        ''', (self.current_session_id,))
        
        feedback_stats = cursor.fetchone()
        
        conn.close()
        
        if action_stats and action_stats[0] > 0:
            total_actions, avg_reward, avg_confidence, successful_actions = action_stats
            success_rate = successful_actions / total_actions if total_actions > 0 else 0
        else:
            total_actions = avg_reward = avg_confidence = success_rate = 0
        
        if feedback_stats:
            positive_feedback, negative_feedback, _ = feedback_stats
            feedback_ratio = positive_feedback / (positive_feedback + negative_feedback) if (positive_feedback + negative_feedback) > 0 else 0
        else:
            positive_feedback = negative_feedback = feedback_ratio = 0
        
        return {
            "session_id": self.current_session_id,
            "total_actions": total_actions,
            "average_reward": avg_reward or 0,
            "average_confidence": avg_confidence or 0,
            "success_rate": success_rate,
            "positive_feedback": positive_feedback,
            "negative_feedback": negative_feedback,
            "feedback_ratio": feedback_ratio,
            "current_episode": self.episode_count
        }
    
    def export_logs(self, format_type: str = "csv") -> str:
        """Export logs in specified format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type.lower() == "csv":
            export_file = os.path.join(self.log_dir, f"export_{timestamp}.csv")
            # Copy the existing CSV
            import shutil
            shutil.copy2(self.action_log_file, export_file)
            return export_file
        
        elif format_type.lower() == "json":
            export_file = os.path.join(self.log_dir, f"export_{timestamp}.json")
            df = pd.read_csv(self.action_log_file)
            df.to_json(export_file, orient="records", indent=2)
            return export_file
        
        else:
            raise ValueError("Unsupported export format. Use 'csv' or 'json'")
    
    def log_confidence_per_task(self, task_id: str, task_description: str, 
                               confidence_score: float, state: str, action: str,
                               q_values: Dict[str, float], normalized_scores: Dict[str, float]):
        """Log detailed confidence information per task to standalone files"""
        try:
            # Normalize confidence score (0-1 range with proper scaling)
            normalized_confidence = max(0.0, min(1.0, confidence_score))
            
            # Create confidence data
            confidence_data = {
                'task_id': task_id,
                'task_description': task_description,
                'timestamp': datetime.now().isoformat(),
                'session_id': self.current_session_id,
                'episode': self.episode_count,
                'state': state,
                'selected_action': action,
                'raw_confidence_score': confidence_score,
                'normalized_confidence': normalized_confidence,
                'confidence_category': self._categorize_confidence(normalized_confidence),
                'q_values': q_values,
                'normalized_q_scores': normalized_scores,
                'confidence_components': self._calculate_confidence_components(q_values, action)
            }
            
            # Save to task-specific CSV
            self._save_task_confidence_csv(confidence_data)
            
            # Save to task-specific JSON
            self._save_task_confidence_json(confidence_data)
            
            print(f"📊 Confidence logged for task {task_id}: {normalized_confidence:.3f} ({confidence_data['confidence_category']})")
            
        except Exception as e:
            print(f"❌ Failed to log confidence for task {task_id}: {e}")
    
    def _categorize_confidence(self, confidence: float) -> str:
        """Categorize confidence score into human-readable categories"""
        if confidence >= 0.8:
            return "High"
        elif confidence >= 0.6:
            return "Medium-High"
        elif confidence >= 0.4:
            return "Medium"
        elif confidence >= 0.2:
            return "Low-Medium"
        else:
            return "Low"
    
    def _calculate_confidence_components(self, q_values: Dict[str, float], selected_action: str) -> Dict[str, float]:
        """Calculate detailed confidence components for transparency"""
        if not q_values or len(q_values) < 2:
            return {
                'q_value_spread': 0.0,
                'action_rank': 0,
                'relative_advantage': 0.0,
                'uncertainty': 1.0
            }
        
        sorted_actions = sorted(q_values.items(), key=lambda x: x[1], reverse=True)
        action_rank = next((i for i, (a, _) in enumerate(sorted_actions) if a == selected_action), -1) + 1
        
        q_vals = list(q_values.values())
        q_spread = max(q_vals) - min(q_vals) if len(q_vals) > 1 else 0.0
        
        selected_q = q_values.get(selected_action, 0.0)
        best_q = sorted_actions[0][1] if sorted_actions else 0.0
        relative_advantage = (selected_q - best_q) if best_q != 0 else 0.0
        
        # Calculate uncertainty (higher spread = lower uncertainty)
        uncertainty = 1.0 - min(q_spread / 2.0, 1.0) if q_spread > 0 else 1.0
        
        return {
            'q_value_spread': q_spread,
            'action_rank': action_rank,
            'relative_advantage': relative_advantage,
            'uncertainty': uncertainty
        }
    
    def _save_task_confidence_csv(self, confidence_data: Dict[str, Any]):
        """Save confidence data to CSV file"""
        confidence_csv_file = os.path.join(self.log_dir, "task_confidence_log.csv")
        
        # Flatten the nested dictionaries for CSV
        flat_data = {
            'task_id': confidence_data['task_id'],
            'task_description': confidence_data['task_description'],
            'timestamp': confidence_data['timestamp'],
            'session_id': confidence_data['session_id'],
            'episode': confidence_data['episode'],
            'state': confidence_data['state'],
            'selected_action': confidence_data['selected_action'],
            'raw_confidence_score': confidence_data['raw_confidence_score'],
            'normalized_confidence': confidence_data['normalized_confidence'],
            'confidence_category': confidence_data['confidence_category'],
            'q_values_json': json.dumps(confidence_data['q_values']),
            'normalized_q_scores_json': json.dumps(confidence_data['normalized_q_scores']),
            'q_value_spread': confidence_data['confidence_components']['q_value_spread'],
            'action_rank': confidence_data['confidence_components']['action_rank'],
            'relative_advantage': confidence_data['confidence_components']['relative_advantage'],
            'uncertainty': confidence_data['confidence_components']['uncertainty']
        }
        
        # Check if file exists and create header if needed
        file_exists = os.path.exists(confidence_csv_file)
        
        with open(confidence_csv_file, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=flat_data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(flat_data)
    
    def _save_task_confidence_json(self, confidence_data: Dict[str, Any]):
        """Save confidence data to JSON file per task"""
        task_id = confidence_data['task_id']
        confidence_json_file = os.path.join(self.log_dir, f"confidence_{task_id}.json")
        
        with open(confidence_json_file, 'w') as jsonfile:
            json.dump(confidence_data, jsonfile, indent=2)
    
    def export_confidence_summary(self, format_type: str = "csv") -> str:
        """Export confidence summary statistics"""
        try:
            conn = sqlite3.connect(self.db_file)
            
            # Get confidence statistics
            query = '''
                SELECT 
                    AVG(confidence_score) as avg_confidence,
                    MIN(confidence_score) as min_confidence,
                    MAX(confidence_score) as max_confidence,
                    COUNT(*) as total_actions,
                    COUNT(CASE WHEN confidence_score >= 0.8 THEN 1 END) as high_confidence,
                    COUNT(CASE WHEN confidence_score >= 0.6 AND confidence_score < 0.8 THEN 1 END) as medium_high_confidence,
                    COUNT(CASE WHEN confidence_score >= 0.4 AND confidence_score < 0.6 THEN 1 END) as medium_confidence,
                    COUNT(CASE WHEN confidence_score < 0.4 THEN 1 END) as low_confidence
                FROM actions 
                WHERE session_id = ?
            '''
            
            cursor = conn.cursor()
            cursor.execute(query, (self.current_session_id,))
            stats = cursor.fetchone()
            
            if stats and stats[3] > 0:  # total_actions > 0
                summary_data = {
                    'session_id': self.current_session_id,
                    'timestamp': datetime.now().isoformat(),
                    'total_actions': stats[3],
                    'avg_confidence': round(stats[0] or 0, 3),
                    'min_confidence': round(stats[1] or 0, 3),
                    'max_confidence': round(stats[2] or 0, 3),
                    'high_confidence_count': stats[4],
                    'medium_high_confidence_count': stats[5],
                    'medium_confidence_count': stats[6],
                    'low_confidence_count': stats[7],
                    'high_confidence_percentage': round((stats[4] / stats[3]) * 100, 1),
                    'medium_high_confidence_percentage': round((stats[5] / stats[3]) * 100, 1),
                    'medium_confidence_percentage': round((stats[6] / stats[3]) * 100, 1),
                    'low_confidence_percentage': round((stats[7] / stats[3]) * 100, 1)
                }
            else:
                summary_data = {'error': 'No confidence data found for current session'}
            
            conn.close()
            
            # Export to specified format
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format_type.lower() == "csv":
                export_file = os.path.join(self.log_dir, f"confidence_summary_{timestamp}.csv")
                df = pd.DataFrame([summary_data])
                df.to_csv(export_file, index=False)
            else:
                export_file = os.path.join(self.log_dir, f"confidence_summary_{timestamp}.json")
                with open(export_file, 'w') as f:
                    json.dump(summary_data, f, indent=2)
            
            return export_file
            
        except Exception as e:
            print(f"❌ Failed to export confidence summary: {e}")
            return ""


# Example usage and testing
if __name__ == "__main__":
    # Test the logger
    logger = Logger()
    
    # Test logging an action
    logger.log_action(
        task_id="TASK_001",
        parsed_intent="open_file",
        action_taken="open_file_browser",
        internal_reward=1.0,
        confidence_score=0.85,
        user_feedback="👍",
        state_representation={"current_app": "desktop", "files_open": 0},
        q_values={"open_file_browser": 0.8, "open_notepad": 0.6},
        next_best_actions=["open_file_browser", "open_notepad"]
    )
    
    # Test episode metrics
    logger.log_episode_metrics(
        total_reward=5.5,
        average_confidence=0.78,
        success_rate=0.9,
        exploration_rate=0.1
    )
    
    # Get summary
    summary = logger.get_session_summary()
    print("Session Summary:", summary)
    
    print("Logger testing completed successfully!")