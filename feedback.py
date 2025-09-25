import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import time
import json

from rl_agent import QLearningAgent
from logger import Logger


class FeedbackSystem:
    """User feedback collection and processing system"""
    
    def __init__(self, agent: QLearningAgent = None):
        self.agent = agent
        self.pending_feedback = {}
        self.feedback_history = []
        
    def collect_cli_feedback(self, task_id: str) -> tuple:
        """Collect feedback through CLI"""
        print("\n" + "="*50)
        print("💬 FEEDBACK REQUEST")
        print("="*50)
        print("How was the agent's action?")
        print("Options:")
        print("  👍 / 'good' / 'positive' - Action was correct")
        print("  👎 / 'bad' / 'negative' - Action was incorrect")
        print("  'skip' - No feedback")
        
        while True:
            feedback_input = input("\nYour feedback: ").strip().lower()
            
            if feedback_input in ['👍', 'good', 'positive', 'yes', 'y']:
                feedback_type = "👍"
                suggested_action = None
                break
            elif feedback_input in ['👎', 'bad', 'negative', 'no', 'n']:
                feedback_type = "👎"
                print("\n🤔 What should the agent have done instead?")
                print("Available actions:", ", ".join(self.agent.available_actions[:10]) + "...")
                suggested_action = input("Suggested action (or press Enter to skip): ").strip()
                if not suggested_action:
                    suggested_action = None
                break
            elif feedback_input in ['skip', 's', '']:
                return None, None
            else:
                print("❌ Invalid input. Please use 👍, 👎, or 'skip'")
        
        return feedback_type, suggested_action
    
    def process_feedback(self, feedback_type: str, suggested_action: str = None) -> dict:
        """Process and apply feedback"""
        if not self.agent:
            return {"error": "No agent available"}
        
        total_reward = self.agent.receive_feedback(feedback_type, suggested_action)
        
        feedback_record = {
            "timestamp": datetime.now(),
            "feedback_type": feedback_type,
            "suggested_action": suggested_action,
            "total_reward": total_reward,
            "task_id": getattr(self.agent, 'current_task_id', 'unknown')
        }
        
        self.feedback_history.append(feedback_record)
        
        return {
            "success": True,
            "total_reward": total_reward,
            "feedback_record": feedback_record
        }
    
    def get_feedback_summary(self) -> dict:
        """Get summary of all feedback"""
        if not self.feedback_history:
            return {
                "total_feedback": 0,
                "positive_count": 0,
                "negative_count": 0,
                "positive_ratio": 0.0,
                "average_reward": 0.0
            }
        
        total = len(self.feedback_history)
        positive = sum(1 for f in self.feedback_history if f["feedback_type"] == "👍")
        negative = sum(1 for f in self.feedback_history if f["feedback_type"] == "👎")
        avg_reward = np.mean([f["total_reward"] for f in self.feedback_history])
        
        return {
            "total_feedback": total,
            "positive_count": positive,
            "negative_count": negative,
            "positive_ratio": positive / total if total > 0 else 0.0,
            "average_reward": avg_reward
        }


def create_streamlit_interface():
    """Create Streamlit web interface for the RL agent"""
    
    st.set_page_config(
        page_title="RL Device Agent v2",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'agent' not in st.session_state:
        st.session_state.agent = QLearningAgent()
        st.session_state.feedback_system = FeedbackSystem(st.session_state.agent)
        st.session_state.task_history = []
        st.session_state.current_task_result = None
    
    # Header
    st.title("🤖 RL Device Agent v2")
    st.markdown("**Reinforcement Learning Device Control Agent with User Feedback**")
    
    # Sidebar for controls and stats
    with st.sidebar:
        st.header("🎛️ Control Panel")
        
        # Agent Statistics
        stats = st.session_state.agent.get_learning_statistics()
        
        st.subheader("📊 Learning Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("States Learned", stats['qtable_stats']['total_states'])
            st.metric("Exploration Rate", f"{stats['qtable_stats']['exploration_rate']:.3f}")
        with col2:
            st.metric("Total Actions", stats['session_stats']['total_actions'])
            st.metric("Avg Reward", f"{stats['session_stats']['average_reward']:.2f}")
        
        # Session Info
        st.subheader("🔍 Session Info")
        st.write(f"**Session ID:** {stats['session_stats']['session_id']}")
        st.write(f"**Success Rate:** {stats['session_stats']['success_rate']:.1%}")
        st.write(f"**Feedback Ratio:** {stats['session_stats']['feedback_ratio']:.1%}")
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        if st.button("🔄 Reset Episode"):
            st.session_state.agent.end_episode()
            st.success("Episode reset!")
            st.rerun()
        
        if st.button("💾 Save Q-table"):
            st.session_state.agent.save_qtable()
            st.success("Q-table saved!")
        
        if st.button("📊 Export Logs"):
            try:
                export_file = st.session_state.agent.logger.export_logs("csv")
                st.success(f"Logs exported to {export_file}")
            except Exception as e:
                st.error(f"Export failed: {e}")
    
    # Main interface tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Task Execution", "📈 Learning Curve", "📋 Action History", "💡 Suggestions"])
    
    with tab1:
        st.header("🎯 Task Execution")
        
        # Task input
        col1, col2 = st.columns([3, 1])
        with col1:
            task_input = st.text_input(
                "Enter a task description:",
                placeholder="e.g., 'open notepad', 'mute audio', 'take screenshot'",
                key="task_input"
            )
        with col2:
            execute_button = st.button("🚀 Execute", type="primary")
        
        # Execute task
        if execute_button and task_input:
            with st.spinner("Executing task..."):
                result = st.session_state.agent.process_task(task_input)
                st.session_state.current_task_result = result
                st.session_state.task_history.append(result)
            
            st.success("Task executed!")
            st.rerun()
        
        # Display current task result
        if st.session_state.current_task_result:
            result = st.session_state.current_task_result
            
            st.subheader("📋 Execution Results")
            
            # Results display
            col1, col2, col3 = st.columns(3)
            with col1:
                status = "✅ Success" if result['execution_success'] else "❌ Failed"
                st.metric("Status", status)
            with col2:
                st.metric("Confidence", f"{result['confidence_score']:.2f}")
            with col3:
                st.metric("Internal Reward", f"{result['internal_reward']:.1f}")
            
            # Details
            with st.expander("📝 Task Details", expanded=True):
                st.write(f"**Task ID:** {result['task_id']}")
                st.write(f"**Parsed Intent:** {result['parsed_intent']}")
                st.write(f"**Selected Action:** {result['selected_action']}")
                st.write(f"**Message:** {result['execution_message']}")
            
            # Next best actions
            if result['next_best_actions']:
                with st.expander("💡 Alternative Actions"):
                    for i, (action, q_value) in enumerate(result['next_best_actions'], 1):
                        st.write(f"{i}. **{action}** (Q-value: {q_value:.2f})")
            
            # Feedback section
            st.subheader("💬 Provide Feedback")
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button("👍 Good Action", key="feedback_positive"):
                    feedback_result = st.session_state.feedback_system.process_feedback("👍")
                    if feedback_result['success']:
                        st.success(f"Positive feedback recorded! Total reward: {feedback_result['total_reward']:.2f}")
                        st.session_state.current_task_result = None
                        st.rerun()
            
            with col2:
                if st.button("👎 Wrong Action", key="feedback_negative"):
                    st.session_state.show_suggestion_input = True
            
            # Suggestion input for negative feedback
            if getattr(st.session_state, 'show_suggestion_input', False):
                with col3:
                    suggested_action = st.selectbox(
                        "What should have been done?",
                        [""] + st.session_state.agent.available_actions,
                        key="suggested_action"
                    )
                    
                    if st.button("Submit Negative Feedback"):
                        suggestion = suggested_action if suggested_action else None
                        feedback_result = st.session_state.feedback_system.process_feedback("👎", suggestion)
                        if feedback_result['success']:
                            st.error(f"Negative feedback recorded! Total reward: {feedback_result['total_reward']:.2f}")
                            st.session_state.current_task_result = None
                            st.session_state.show_suggestion_input = False
                            st.rerun()
    
    with tab2:
        st.header("📈 Learning Curve")
        
        # Get learning history
        learning_df = st.session_state.agent.logger.get_learning_history()
        
        if not learning_df.empty:
            # Learning curve chart
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            # Total reward over episodes
            ax1.plot(learning_df['episode'], learning_df['total_reward'], 'b-', marker='o', linewidth=2)
            ax1.set_title('Total Reward per Episode')
            ax1.set_xlabel('Episode')
            ax1.set_ylabel('Total Reward')
            ax1.grid(True, alpha=0.3)
            
            # Average confidence over episodes
            ax2.plot(learning_df['episode'], learning_df['average_confidence'], 'g-', marker='s', linewidth=2)
            ax2.set_title('Average Confidence per Episode')
            ax2.set_xlabel('Episode')
            ax2.set_ylabel('Confidence Score')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # Save learning curve
            if st.button("💾 Save Learning Curve"):
                fig.savefig('logs/learning_curve.png', dpi=300, bbox_inches='tight')
                st.success("Learning curve saved to logs/learning_curve.png")
            
            # Learning statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Episodes", len(learning_df))
            with col2:
                avg_reward = learning_df['total_reward'].mean()
                st.metric("Average Reward", f"{avg_reward:.2f}")
            with col3:
                avg_confidence = learning_df['average_confidence'].mean()
                st.metric("Average Confidence", f"{avg_confidence:.2f}")
        
        else:
            st.info("No learning data available yet. Execute some tasks to see the learning curve!")
    
    with tab3:
        st.header("📋 Action History")
        
        # Get recent actions
        action_df = st.session_state.agent.logger.get_action_history(50)
        
        if not action_df.empty:
            # Display as table
            st.dataframe(
                action_df,
                column_config={
                    "timestamp": st.column_config.DatetimeColumn("Time"),
                    "task_id": "Task ID",
                    "parsed_intent": "Intent",
                    "action_taken": "Action",
                    "total_reward": st.column_config.NumberColumn("Reward", format="%.2f"),
                    "confidence_score": st.column_config.NumberColumn("Confidence", format="%.2f"),
                    "user_feedback": "Feedback"
                },
                hide_index=True
            )
            
            # Summary statistics
            st.subheader("📊 Summary Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Actions", len(action_df))
            with col2:
                avg_reward = action_df['total_reward'].mean()
                st.metric("Avg Reward", f"{avg_reward:.2f}")
            with col3:
                avg_confidence = action_df['confidence_score'].mean()
                st.metric("Avg Confidence", f"{avg_confidence:.2f}")
            with col4:
                positive_feedback = len(action_df[action_df['user_feedback'] == '👍'])
                total_feedback = len(action_df[action_df['user_feedback'].notna()])
                ratio = positive_feedback / total_feedback if total_feedback > 0 else 0
                st.metric("👍 Feedback Ratio", f"{ratio:.1%}")
        
        else:
            st.info("No action history available yet.")
    
    with tab4:
        st.header("💡 Action Suggestions")
        
        # Context input for suggestions
        context_input = st.text_input(
            "Context for suggestions (optional):",
            placeholder="e.g., 'working with files', 'audio problems'"
        )
        
        if st.button("🔮 Get Suggestions"):
            suggestions = st.session_state.agent.suggest_next_actions(context_input)
            
            st.subheader("🎯 Recommended Actions")
            
            for i, (action, confidence, reasoning) in enumerate(suggestions, 1):
                with st.expander(f"{i}. **{action}** (Confidence: {confidence:.2f})"):
                    st.write(f"**Reasoning:** {reasoning}")
                    
                    if st.button(f"Execute {action}", key=f"suggest_exec_{i}"):
                        result = st.session_state.agent.process_task(action)
                        st.session_state.current_task_result = result
                        st.session_state.task_history.append(result)
                        st.success(f"Executed {action}!")
                        st.rerun()
        
        # Q-value visualization
        if st.session_state.agent.q_table:
            st.subheader("🧠 Q-Table Insights")
            
            # Most confident actions
            all_confidences = []
            for state in st.session_state.agent.q_table:
                for action in st.session_state.agent.q_table[state]:
                    confidence = st.session_state.agent._calculate_confidence_score(state, action)
                    all_confidences.append({
                        'state': state,
                        'action': action,
                        'q_value': st.session_state.agent.q_table[state][action],
                        'confidence': confidence
                    })
            
            if all_confidences:
                confidence_df = pd.DataFrame(all_confidences)
                top_confident = confidence_df.nlargest(10, 'confidence')
                
                st.write("**Top 10 Most Confident State-Action Pairs:**")
                st.dataframe(
                    top_confident[['state', 'action', 'confidence', 'q_value']],
                    column_config={
                        'confidence': st.column_config.NumberColumn("Confidence", format="%.3f"),
                        'q_value': st.column_config.NumberColumn("Q-Value", format="%.3f")
                    },
                    hide_index=True
                )


def main():
    """Main function to run Streamlit app"""
    create_streamlit_interface()


if __name__ == "__main__":
    main()