import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from datetime import datetime, timedelta
import os
from typing import List, Dict, Tuple, Optional
import sqlite3


class LearningVisualizer:
    """Learning curve and reward tracking visualization system"""
    
    def __init__(self, logger=None, save_dir: str = "logs"):
        self.logger = logger
        self.save_dir = save_dir
        
        # Set up matplotlib style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create save directory
        os.makedirs(save_dir, exist_ok=True)
    
    def plot_learning_curve(self, 
                           episodes: List[int] = None,
                           rewards: List[float] = None,
                           confidences: List[float] = None,
                           success_rates: List[float] = None,
                           save_path: str = None) -> str:
        """
        Plot comprehensive learning curve with multiple metrics
        
        Returns:
            Path to saved plot
        """
        # Get data from logger if not provided
        if episodes is None and self.logger:
            df = self.logger.get_learning_history()
            if not df.empty:
                episodes = df['episode'].tolist()
                rewards = df['total_reward'].tolist()
                confidences = df['average_confidence'].tolist()
                success_rates = df['success_rate'].tolist()
        
        if not episodes or len(episodes) == 0:
            print("No learning data available for plotting")
            return None
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('RL Device Agent v2 - Learning Progress', fontsize=16, fontweight='bold')
        
        # 1. Total Reward per Episode
        ax1.plot(episodes, rewards, 'b-', marker='o', linewidth=2, markersize=4)
        ax1.set_title('Total Reward per Episode', fontweight='bold')
        ax1.set_xlabel('Episode')
        ax1.set_ylabel('Total Reward')
        ax1.grid(True, alpha=0.3)
        
        # Add trend line
        if len(episodes) > 1:
            z = np.polyfit(episodes, rewards, 1)
            p = np.poly1d(z)
            ax1.plot(episodes, p(episodes), "r--", alpha=0.8, linewidth=1, label=f'Trend: {z[0]:.3f}x + {z[1]:.2f}')
            ax1.legend()
        
        # 2. Average Confidence per Episode
        ax2.plot(episodes, confidences, 'g-', marker='s', linewidth=2, markersize=4)
        ax2.set_title('Average Confidence per Episode', fontweight='bold')
        ax2.set_xlabel('Episode')
        ax2.set_ylabel('Confidence Score')
        ax2.set_ylim(0, 1)
        ax2.grid(True, alpha=0.3)
        
        # 3. Success Rate per Episode
        ax3.plot(episodes, success_rates, 'orange', marker='^', linewidth=2, markersize=4)
        ax3.set_title('Success Rate per Episode', fontweight='bold')
        ax3.set_xlabel('Episode')
        ax3.set_ylabel('Success Rate')
        ax3.set_ylim(0, 1)
        ax3.grid(True, alpha=0.3)
        
        # 4. Combined Performance Score
        # Combine reward (normalized), confidence, and success rate
        if len(rewards) > 0:
            norm_rewards = [(r - min(rewards)) / (max(rewards) - min(rewards)) if max(rewards) != min(rewards) else 0.5 for r in rewards]
            performance_scores = [(nr * 0.4 + c * 0.3 + sr * 0.3) for nr, c, sr in zip(norm_rewards, confidences, success_rates)]
            
            ax4.plot(episodes, performance_scores, 'purple', marker='D', linewidth=2, markersize=4)
            ax4.set_title('Combined Performance Score', fontweight='bold')
            ax4.set_xlabel('Episode')
            ax4.set_ylabel('Performance Score')
            ax4.set_ylim(0, 1)
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(self.save_dir, f"learning_curve_{timestamp}.png")
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"📊 Learning curve saved to: {save_path}")
        return save_path
    
    def plot_reward_distribution(self, save_path: str = None) -> str:
        """Plot reward distribution histogram"""
        if not self.logger:
            return None
        
        # Get action history
        df = self.logger.get_action_history(1000)
        
        if df.empty:
            print("No action data available for reward distribution")
            return None
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle('Reward Distribution Analysis', fontsize=14, fontweight='bold')
        
        # 1. Reward histogram
        ax1.hist(df['total_reward'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.set_title('Distribution of Total Rewards')
        ax1.set_xlabel('Total Reward')
        ax1.set_ylabel('Frequency')
        ax1.grid(True, alpha=0.3)
        
        # Add statistics
        mean_reward = df['total_reward'].mean()
        std_reward = df['total_reward'].std()
        ax1.axvline(mean_reward, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_reward:.2f}')
        ax1.legend()
        
        # 2. Confidence vs Reward scatter
        ax2.scatter(df['confidence_score'], df['total_reward'], alpha=0.6, c='green', s=30)
        ax2.set_title('Confidence vs Total Reward')
        ax2.set_xlabel('Confidence Score')
        ax2.set_ylabel('Total Reward')
        ax2.grid(True, alpha=0.3)
        
        # Add correlation line
        if len(df) > 1:
            z = np.polyfit(df['confidence_score'], df['total_reward'], 1)
            p = np.poly1d(z)
            ax2.plot(df['confidence_score'], p(df['confidence_score']), "r--", alpha=0.8)
            
            # Calculate correlation
            correlation = df['confidence_score'].corr(df['total_reward'])
            ax2.text(0.05, 0.95, f'Correlation: {correlation:.3f}', transform=ax2.transAxes, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.5))
        
        plt.tight_layout()
        
        # Save plot
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(self.save_dir, f"reward_distribution_{timestamp}.png")
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"📊 Reward distribution plot saved to: {save_path}")
        return save_path
    
    def plot_action_frequency(self, save_path: str = None) -> str:
        """Plot action frequency and success rates"""
        if not self.logger:
            return None
        
        # Get action history
        df = self.logger.get_action_history(1000)
        
        if df.empty:
            print("No action data available for frequency analysis")
            return None
        
        # Analyze action frequencies and success rates
        action_stats = df.groupby('action_taken').agg({
            'task_id': 'count',
            'total_reward': ['mean', 'std'],
            'confidence_score': 'mean'
        }).round(3)
        
        action_stats.columns = ['frequency', 'avg_reward', 'reward_std', 'avg_confidence']
        action_stats = action_stats.sort_values('frequency', ascending=True)
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        fig.suptitle('Action Analysis', fontsize=14, fontweight='bold')
        
        # 1. Action frequency (horizontal bar chart)
        top_actions = action_stats.tail(15)  # Top 15 most frequent actions
        y_pos = np.arange(len(top_actions))
        
        bars1 = ax1.barh(y_pos, top_actions['frequency'], color='lightcoral', alpha=0.7)
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(top_actions.index, fontsize=10)
        ax1.set_xlabel('Frequency')
        ax1.set_title('Most Frequent Actions')
        ax1.grid(True, alpha=0.3, axis='x')
        
        # Add frequency labels
        for i, bar in enumerate(bars1):
            width = bar.get_width()
            ax1.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                    f'{int(width)}', ha='left', va='center', fontsize=9)
        
        # 2. Average reward by action
        bars2 = ax2.barh(y_pos, top_actions['avg_reward'], color='lightgreen', alpha=0.7)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(top_actions.index, fontsize=10)
        ax2.set_xlabel('Average Reward')
        ax2.set_title('Average Reward per Action')
        ax2.grid(True, alpha=0.3, axis='x')
        
        # Add reward labels
        for i, bar in enumerate(bars2):
            width = bar.get_width()
            ax2.text(width + 0.02, bar.get_y() + bar.get_height()/2, 
                    f'{width:.2f}', ha='left', va='center', fontsize=9)
        
        plt.tight_layout()
        
        # Save plot
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(self.save_dir, f"action_analysis_{timestamp}.png")
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"📊 Action analysis plot saved to: {save_path}")
        return save_path
    
    def plot_feedback_timeline(self, save_path: str = None) -> str:
        """Plot feedback timeline and patterns"""
        if not self.logger:
            return None
        
        # Get action history with feedback
        df = self.logger.get_action_history(1000)
        feedback_df = df[df['user_feedback'].notna()].copy()
        
        if feedback_df.empty:
            print("No feedback data available for timeline analysis")
            return None
        
        # Convert timestamp to datetime
        feedback_df['timestamp'] = pd.to_datetime(feedback_df['timestamp'])
        feedback_df = feedback_df.sort_values('timestamp')
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle('Feedback Timeline Analysis', fontsize=14, fontweight='bold')
        
        # 1. Feedback timeline
        positive_feedback = feedback_df[feedback_df['user_feedback'] == '👍']
        negative_feedback = feedback_df[feedback_df['user_feedback'] == '👎']
        
        ax1.scatter(positive_feedback['timestamp'], positive_feedback['total_reward'], 
                   color='green', marker='o', s=50, alpha=0.7, label='👍 Positive')
        ax1.scatter(negative_feedback['timestamp'], negative_feedback['total_reward'], 
                   color='red', marker='x', s=50, alpha=0.7, label='👎 Negative')
        
        ax1.set_title('Feedback Timeline')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Total Reward')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Rotate x-axis labels
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # 2. Cumulative feedback ratio
        feedback_df['positive'] = (feedback_df['user_feedback'] == '👍').astype(int)
        feedback_df['cumulative_positive'] = feedback_df['positive'].cumsum()
        feedback_df['cumulative_total'] = range(1, len(feedback_df) + 1)
        feedback_df['feedback_ratio'] = feedback_df['cumulative_positive'] / feedback_df['cumulative_total']
        
        ax2.plot(feedback_df['timestamp'], feedback_df['feedback_ratio'], 
                color='blue', linewidth=2, marker='o', markersize=3)
        ax2.set_title('Cumulative Positive Feedback Ratio')
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Positive Feedback Ratio')
        ax2.set_ylim(0, 1)
        ax2.grid(True, alpha=0.3)
        
        # Rotate x-axis labels
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        # Add final ratio text
        final_ratio = feedback_df['feedback_ratio'].iloc[-1]
        ax2.text(0.02, 0.98, f'Final Ratio: {final_ratio:.2%}', transform=ax2.transAxes, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7),
                verticalalignment='top')
        
        plt.tight_layout()
        
        # Save plot
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(self.save_dir, f"feedback_timeline_{timestamp}.png")
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"📊 Feedback timeline plot saved to: {save_path}")
        return save_path
    
    def create_comprehensive_report(self, save_dir: str = None) -> Dict[str, str]:
        """Create comprehensive visual report with all charts"""
        if save_dir is None:
            save_dir = self.save_dir
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = os.path.join(save_dir, f"report_{timestamp}")
        os.makedirs(report_dir, exist_ok=True)
        
        plots = {}
        
        try:
            # Generate all plots
            plots['learning_curve'] = self.plot_learning_curve(
                save_path=os.path.join(report_dir, "learning_curve.png")
            )
            
            plots['reward_distribution'] = self.plot_reward_distribution(
                save_path=os.path.join(report_dir, "reward_distribution.png")
            )
            
            plots['action_analysis'] = self.plot_action_frequency(
                save_path=os.path.join(report_dir, "action_analysis.png")
            )
            
            plots['feedback_timeline'] = self.plot_feedback_timeline(
                save_path=os.path.join(report_dir, "feedback_timeline.png")
            )
            
            # Create summary statistics file
            if self.logger:
                summary = self.logger.get_session_summary()
                summary_file = os.path.join(report_dir, "summary_stats.txt")
                
                with open(summary_file, 'w') as f:
                    f.write("RL Device Agent v2 - Session Summary\n")
                    f.write("=" * 40 + "\n\n")
                    f.write(f"Session ID: {summary['session_id']}\n")
                    f.write(f"Total Actions: {summary['total_actions']}\n")
                    f.write(f"Average Reward: {summary['average_reward']:.3f}\n")
                    f.write(f"Average Confidence: {summary['average_confidence']:.3f}\n")
                    f.write(f"Success Rate: {summary['success_rate']:.1%}\n")
                    f.write(f"Positive Feedback: {summary['positive_feedback']}\n")
                    f.write(f"Negative Feedback: {summary['negative_feedback']}\n")
                    f.write(f"Feedback Ratio: {summary['feedback_ratio']:.1%}\n")
                    f.write(f"Current Episode: {summary['current_episode']}\n")
                    f.write(f"\nReport Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                plots['summary'] = summary_file
            
            print(f"📊 Comprehensive report generated in: {report_dir}")
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
        
        return plots
    
    def plot_realtime_metrics(self, window_size: int = 50) -> None:
        """Plot real-time metrics for monitoring (for use in Streamlit)"""
        if not self.logger:
            return None
        
        # Get recent data
        df = self.logger.get_action_history(window_size)
        
        if df.empty:
            return None
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Calculate rolling metrics
        df['rolling_reward'] = df['total_reward'].rolling(window=min(10, len(df))).mean()
        df['rolling_confidence'] = df['confidence_score'].rolling(window=min(10, len(df))).mean()
        
        return df


# Example usage and testing
if __name__ == "__main__":
    from logger import Logger
    
    # Test the visualizer
    logger = Logger()
    visualizer = LearningVisualizer(logger)
    
    # Generate some sample data for testing
    print("Generating sample data for testing...")
    
    # Simulate some learning episodes
    for episode in range(1, 11):
        for action_num in range(1, 6):
            logger.log_action(
                task_id=f"TEST_{episode}_{action_num}",
                parsed_intent=f"test_intent_{action_num}",
                action_taken=f"test_action_{action_num}",
                internal_reward=np.random.normal(0.5, 0.3),
                confidence_score=min(1.0, max(0.0, np.random.normal(0.6, 0.2))),
                user_feedback=np.random.choice(["👍", "👎", None], p=[0.6, 0.2, 0.2]),
                action_success=np.random.choice([True, False], p=[0.8, 0.2])
            )
        
        # Log episode metrics
        logger.log_episode_metrics(
            total_reward=np.random.normal(2.0, 1.0),
            average_confidence=min(1.0, max(0.0, np.random.normal(0.6, 0.15))),
            success_rate=np.random.uniform(0.6, 0.9),
            exploration_rate=max(0.01, 0.2 - episode * 0.015)
        )
    
    print("Sample data generated!")
    
    # Test all visualization functions
    print("\nTesting visualization functions...")
    
    learning_curve_path = visualizer.plot_learning_curve()
    reward_dist_path = visualizer.plot_reward_distribution()
    action_freq_path = visualizer.plot_action_frequency()
    feedback_timeline_path = visualizer.plot_feedback_timeline()
    
    # Generate comprehensive report
    report_paths = visualizer.create_comprehensive_report()
    
    print("\n✅ All visualization tests completed!")
    print("Generated files:")
    for key, path in report_paths.items():
        if path:
            print(f"  {key}: {path}")