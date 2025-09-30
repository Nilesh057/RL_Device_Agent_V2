# RL Device Agent v2 - Production Documentation

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [System Architecture](#system-architecture)
3. [API Reference](#api-reference)
4. [Configuration](#configuration)
5. [Sample JSON I/O](#sample-json-io)
6. [Reward Formula](#reward-formula)
7. [Learning Curve Examples](#learning-curve-examples)
8. [CLI Usage](#cli-usage)
9. [Streamlit Dashboard](#streamlit-dashboard)
10. [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Optional: Voice input support
pip install SpeechRecognition pyaudio
```

### Basic Usage

```python
from rl_agent import QLearningAgent

# Initialize agent
agent = QLearningAgent()

# Process a task
result = agent.process_task("take screenshot")

# Provide feedback
agent.receive_feedback("👍")  # or "👎" with optional suggestion

# End learning episode
agent.end_episode()
```

### Command Line Interface

```bash
# Run CLI interface
python rl_agent.py

# Run demo system
python demo.py

# Launch web dashboard
streamlit run streamlit_app.py
```

## 🏗️ System Architecture

### Core Components

1. **QLearningAgent**: Main reinforcement learning engine
2. **DeviceActions**: System action execution layer
3. **Logger**: Comprehensive logging and metrics
4. **TaskScenarios**: Demo and testing scenarios
5. **Visualizer**: Learning curve generation
6. **FeedbackSystem**: User interaction handling

### Data Flow

```
User Input → Intent Parsing → State Representation → Action Selection → 
Execution → Logging → User Feedback → Q-Table Update → Learning
```

### File Structure

```
RL_Device_Agent_V2/
├── rl_agent.py          # Core RL implementation
├── device_actions.py    # System actions (54+ commands)
├── logger.py            # CSV/SQLite logging
├── task_scenarios.py    # Task generation & demos
├── visualizer.py        # Learning visualization
├── feedback.py          # User feedback system
├── demo.py              # Production demo runner
├── streamlit_app.py     # Web dashboard
├── voice_input.py       # Voice command support
├── models/              # Saved Q-tables
└── logs/                # Execution logs & reports
```

## 📖 API Reference

### QLearningAgent Class

#### Initialization

```python
agent = QLearningAgent(
    learning_rate=0.1,        # Q-learning rate
    discount_factor=0.9,      # Future reward discount
    epsilon=0.2,              # Exploration rate
    epsilon_decay=0.995,      # Exploration decay
    epsilon_min=0.01,         # Minimum exploration
    qtable_file="models/qtable.pkl"  # Persistence file
)
```

#### Key Methods

```python
# Task Processing
result = agent.process_task(
    task_description="take screenshot",
    context={"user_intent": "productivity"}
)

# Feedback Handling
total_reward = agent.receive_feedback(
    feedback="👎",                    # "👍", "👎", "positive", "negative"
    suggested_action="open_browser"   # Correct action suggestion
)

# Episode Management
agent.end_episode()                   # Complete learning episode
agent.save_qtable()                  # Persist learning state
stats = agent.get_learning_statistics()  # Get metrics

# Action Suggestions
suggestions = agent.suggest_next_actions(
    current_context="productivity task"
)
```

### DeviceActions Class

#### Available Actions (54+ Total)

```python
actions = DeviceActions()
available = actions.get_available_actions()

# Categories:
# - File Operations: open_file_browser, create_new_file, delete_file
# - Audio Control: mute_audio, volume_up, volume_down
# - System Operations: take_screenshot, show_system_info, lock_screen
# - Application Control: open_browser, open_calculator, open_calendar
# - Window Management: minimize_all_windows, close_active_window
# - Task Management: open_task_manager, show_running_processes
```

#### Execution

```python
success, message, info = actions.execute_action(
    action_name="take_screenshot",
    **kwargs  # Action-specific parameters
)
```

## ⚙️ Configuration

### Q-Learning Parameters

```python
# Learning Configuration
LEARNING_RATE = 0.1      # How fast to update Q-values
DISCOUNT_FACTOR = 0.9    # Future reward importance
EPSILON = 0.2            # Initial exploration rate
EPSILON_DECAY = 0.995    # Exploration reduction per episode
EPSILON_MIN = 0.01       # Minimum exploration rate

# Confidence Score Weights
SOFTMAX_WEIGHT = 0.6     # Q-value confidence weight
EXPERIENCE_WEIGHT = 0.25 # Action experience weight
SPREAD_WEIGHT = 0.15     # Q-value spread weight
```

### Logging Configuration

```python
# Log Storage
LOG_DIR = "logs/"
CSV_LOG = "action_log.csv"
SQLITE_DB = "agent_data.db"
TASK_LOG = "task_log.txt"

# Log Fields (CSV/SQLite)
REQUIRED_FIELDS = [
    "timestamp", "task_id", "parsed_intent", "action_taken",
    "internal_reward", "user_feedback", "total_reward",
    "confidence_score", "suggested_correct_action"
]
```

## 📄 Sample JSON I/O

### Task Processing Input

```json
{
    "task_description": "open notepad and create a document",
    "context": {
        "user_intent": "productivity",
        "session_type": "work",
        "priority": "high"
    }
}
```

### Task Processing Output

```json
{
    "task_id": "TASK_20241225_143052_7834",
    "parsed_intent": "open_notepad",
    "selected_action": "open_text_editor",
    "confidence_score": 0.87,
    "next_best_actions": [
        {"action": "open_file_browser", "q_value": 0.65},
        {"action": "create_new_file", "q_value": 0.42}
    ],
    "execution_success": true,
    "execution_message": "Text editor opened successfully",
    "execution_info": {"action_type": "application"},
    "internal_reward": 1.0,
    "state": "intent_open_notepad",
    "q_values": {
        "open_text_editor": 2.34,
        "open_file_browser": 1.56,
        "create_new_file": 0.89
    }
}
```

### Feedback Input

```json
{
    "feedback": "👎",
    "suggested_action": "open_file_browser",
    "reasoning": "User wanted file browser, not text editor"
}
```

### Feedback Output

```json
{
    "total_reward": 0.5,
    "feedback_processed": true,
    "q_table_updated": true,
    "wrong_action_penalty": -1.0,
    "correct_action_boost": 1.5,
    "new_exploration_rate": 0.197
}
```

### Learning Statistics Output

```json
{
    "qtable_stats": {
        "total_states": 15,
        "total_state_action_pairs": 127,
        "most_visited_states": [
            ["intent_take_screenshot", 8],
            ["intent_open_notepad", 6],
            ["intent_mute_audio", 4]
        ],
        "exploration_rate": 0.197,
        "learning_rate": 0.1,
        "discount_factor": 0.9
    },
    "session_stats": {
        "session_id": "20241225_140000",
        "total_actions": 23,
        "positive_feedback": 15,
        "negative_feedback": 8,
        "average_reward": 1.34,
        "success_rate": 0.87,
        "average_confidence": 0.72,
        "feedback_ratio": 0.91
    },
    "learning_history": [
        {
            "episode": 1,
            "total_reward": 12.5,
            "average_confidence": 0.68,
            "success_rate": 0.80,
            "exploration_rate": 0.199
        }
    ]
}
```

## 🧮 Reward Formula

### Total Reward Calculation

```
Total Reward = Internal Reward + Feedback Reward + Bonus/Penalty
```

### Components

#### Internal Reward
```python
# Success-based rewards
if execution_success:
    internal_reward = 1.0
    # Complexity bonus
    if action in ["take_screenshot", "show_system_info"]:
        internal_reward = 1.5
else:
    internal_reward = -1.0
    # Basic action penalty
    if action in ["open_file_browser", "open_notepad"]:
        internal_reward = -1.5
```

#### Feedback Reward
```python
# User feedback rewards
feedback_rewards = {
    "👍": +0.5,    # Positive feedback
    "👎": -0.5,    # Negative feedback
}
```

#### Learning Updates
```python
# Q-Learning Update Formula
Q(s,a) = Q(s,a) + α[r + γ * max(Q(s',a')) - Q(s,a)]

# Where:
# α = learning_rate (0.1)
# r = reward
# γ = discount_factor (0.9)
# s = current state
# a = action taken
# s' = next state
```

#### Enhanced Feedback Handling
```python
# Wrong action penalty (negative feedback with suggestion)
wrong_action_penalty = -1.0
correct_action_boost = +1.5

# Applied when user provides "👎" with suggested correct action
```

### Confidence Score Formula

```python
# Softmax-based confidence (primary component)
confidence_softmax = exp(Q(s,a)) / sum(exp(Q(s,a_i)) for all actions)

# Experience factor
experience_factor = min(action_count / (state_visits * 0.3), 1.0)

# Q-value spread factor
spread_factor = min(std(Q_values) / 2.0, 0.3)

# Final confidence score
confidence = (
    confidence_softmax * 0.6 +
    experience_factor * 0.25 +
    spread_factor * 0.15
)
```

## 📊 Learning Curve Examples

### Sample Learning Progression

```
Episode 1: Total Reward = 8.5,  Confidence = 0.45, Success = 70%
Episode 2: Total Reward = 12.0, Confidence = 0.62, Success = 80%
Episode 3: Total Reward = 15.5, Confidence = 0.73, Success = 90%
Episode 4: Total Reward = 18.0, Confidence = 0.81, Success = 95%
Episode 5: Total Reward = 20.5, Confidence = 0.87, Success = 95%
```

### Generated Visualizations

The system automatically generates:

1. **Learning Curve Plot** (`learning_curve_TIMESTAMP.png`)
   - Total reward per episode
   - Average confidence progression
   - Success rate trend
   - Combined performance score

2. **Reward Distribution** (`reward_distribution_TIMESTAMP.png`)
   - Reward histogram
   - Confidence vs reward correlation

3. **Action Analysis** (`action_analysis_TIMESTAMP.png`)
   - Action frequency chart
   - Success rates by action
   - Confidence trends

## 💻 CLI Usage

### Basic Commands

```bash
# Start CLI interface
python rl_agent.py

# Available commands in CLI:
# - Type task descriptions: "open notepad", "mute audio"
# - "stats" - Show learning statistics
# - "suggest" - Get action suggestions
# - "quit" - Exit application
```

### Example CLI Session

```
🤖 RL Device Agent v2 - Command Line Interface
==================================================

🎯 Enter task or command: take screenshot

🎯 Task TASK_20241225_143052_7834: 'take screenshot'
📝 Parsed Intent: take_screenshot
🔍 State: intent_take_screenshot
🤖 Selected Action: take_screenshot (Confidence: 0.87)
💡 Next Best Actions: ['show_system_info(0.65)', 'open_browser(0.42)']
⚡ Execution: ✅ Success
📋 Message: Screenshot saved as screenshot_20241225_143052.png
🎁 Internal Reward: 1.5

💬 Provide feedback (👍/👎/skip): 👍
👍 Positive feedback received! (+0.5)
🎯 Total Reward: 2.00
📊 Q-value updated for state 'intent_take_screenshot', action 'take_screenshot'
🔍 Exploration rate: 0.197

🎯 Enter task or command: stats

📊 Learning Statistics:
States learned: 8
State-action pairs: 45
Exploration rate: 0.197
Session actions: 12
Average reward: 1.67
```

## 🌐 Streamlit Dashboard

### Features

- **Real-time Task Execution**: Interactive task input and execution
- **Live Learning Metrics**: Q-table size, exploration rate, success rates
- **Visual Learning Curves**: Automatic chart generation
- **Action History Table**: Detailed execution logs
- **Feedback Interface**: Point-and-click feedback collection

### Usage

```bash
# Launch dashboard
streamlit run streamlit_app.py

# Access at: http://localhost:8501
```

### Dashboard Sections

1. **Task Execution Tab**: Input tasks and see results
2. **Learning Curve Tab**: Visual progress tracking
3. **Action History Tab**: Detailed execution logs
4. **Suggestions Tab**: AI-powered action recommendations

## 🔧 Troubleshooting

### Common Issues

#### Q-table Not Persisting
```bash
# Check file permissions
ls -la models/qtable.pkl

# Verify directory exists
mkdir -p models

# Test save/load manually
python -c "from rl_agent import QLearningAgent; agent = QLearningAgent(); agent.save_qtable()"
```

#### Low Confidence Scores
- **Cause**: Insufficient training data
- **Solution**: Run more episodes with diverse tasks
- **Check**: Ensure Q-table has multiple states and actions

```python
# Check Q-table size
stats = agent.get_learning_statistics()
print(f"States: {stats['qtable_stats']['total_states']}")
print(f"Actions: {stats['qtable_stats']['total_state_action_pairs']}")
```

#### Action Execution Failures
- **Cause**: Platform compatibility or permissions
- **Solution**: Check OS-specific implementations in `device_actions.py`

```python
# Test individual actions
from device_actions import DeviceActions
actions = DeviceActions()
success, msg, info = actions.execute_action("show_system_info")
print(f"Success: {success}, Message: {msg}")
```

#### Import Errors
```bash
# Check Python environment
python --version
pip list

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Performance Optimization

#### Memory Usage
- Q-table size grows with state diversity
- Monitor with `agent.get_learning_statistics()`
- Consider state space reduction for large deployments

#### Training Speed
- Reduce exploration rate for faster convergence
- Use pre-trained Q-tables for similar domains
- Batch multiple episodes for efficiency

### Logging Debug

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check log files
ls -la logs/
tail -f logs/action_log.csv
```

## 📞 Support & Contact

For issues, feature requests, or questions:

1. Check troubleshooting section above
2. Review log files in `logs/` directory
3. Run `python test_vscode.py` for system validation
4. Check Q-table persistence with `agent.save_qtable()`

---

**RL Device Agent v2** - Production-Ready Reinforcement Learning System
*Last Updated: 2024-12-25*