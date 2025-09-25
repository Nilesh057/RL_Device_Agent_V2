# RL Device Agent v2 - VS Code Setup Guide

## 🚀 Quick Start

This project is now fully compatible with VS Code and ready to run! Follow these steps to get started:

### 1. Prerequisites

- **Python 3.8+** (Python 3.10+ recommended)
- **VS Code** with Python extension installed
- **Terminal access** (VS Code integrated terminal works perfectly)

### 2. Environment Setup

```bash
# Clone or navigate to the project directory
cd /Users/rupesh/RL_Device_Agent_V2

# Install required dependencies
pip install -r requirements.txt

# Optional: Install voice input dependencies
pip install SpeechRecognition pyaudio
```

### 3. Running in VS Code

#### Option A: Direct Execution
1. Open VS Code in the project directory
2. Open the integrated terminal (`Ctrl+` ` or `View > Terminal`)
3. Run the main demo:
   ```bash
   python demo.py
   ```

#### Option B: Using VS Code Python Debugger
1. Open `demo.py` in VS Code
2. Set breakpoints if needed
3. Press `F5` or click "Run and Debug"
4. Select "Python File" when prompted

#### Option C: Individual Components
```bash
# Run the RL agent CLI
python rl_agent.py

# Run the Streamlit web dashboard
streamlit run streamlit_app.py

# Test voice input (if dependencies installed)
python voice_input.py

# Run compatibility tests
python test_vscode.py
```

## 🎯 Demo Options

When you run `python demo.py`, you'll see these options:

1. **🎬 Complete System Demo** - Full showcase of all features
2. **⚡ Quick Functionality Test** - Fast basic functionality check
3. **🌐 Launch Streamlit Dashboard** - Web-based interface
4. **🎤 Test Voice Input** - Voice command testing
5. **📊 Generate Sample Reports** - Create learning visualizations
6. **🔍 Check System Requirements** - Verify all dependencies
7. **📖 View Documentation** - Access help files
8. **🚪 Exit** - Close the application

## ✅ Verified Working Features

All tests pass successfully:

- ✅ **Import Test**: All modules load correctly
- ✅ **Basic Functionality**: RL agent processes tasks and learns
- ✅ **Device Actions**: 54+ system actions available
- ✅ **Demo Runner**: Automated demonstrations work
- ✅ **Logging System**: Comprehensive action logging
- ✅ **Q-Learning**: Persistent learning with confidence scoring
- ✅ **Feedback Loop**: User feedback integration
- ✅ **Visualization**: Learning curves and progress charts

## 🛠️ VS Code Configuration

### Recommended Extensions

- **Python** (Microsoft) - Essential for Python development
- **Pylance** - Enhanced Python language support
- **Python Debugger** - Debugging support

### Workspace Settings

The project works with default VS Code Python settings. If you encounter issues, ensure:

1. Python interpreter is correctly selected (`Ctrl+Shift+P` → "Python: Select Interpreter")
2. Working directory is set to the project root
3. Required packages are installed in the active Python environment

## 📊 File Structure

```
RL_Device_Agent_V2/
├── demo.py              # Main demo launcher
├── rl_agent.py          # Core RL agent
├── device_actions.py    # System action implementations
├── task_scenarios.py    # Demo scenarios and tasks
├── visualizer.py        # Learning visualization
├── logger.py            # Comprehensive logging
├── voice_input.py       # Voice input handler
├── streamlit_app.py     # Web dashboard
├── feedback.py          # User feedback system
├── test_vscode.py       # VS Code compatibility tests
├── requirements.txt     # Python dependencies
├── logs/                # Generated logs and reports
└── models/              # Saved Q-tables and models
```

## 🎮 Usage Examples

### Basic Task Processing
```python
from rl_agent import QLearningAgent

agent = QLearningAgent()
result = agent.process_task("take screenshot")
agent.receive_feedback("👍")  # User feedback
agent.end_episode()
```

### Device Actions
```python
from device_actions import DeviceActions

actions = DeviceActions()
success, message, info = actions.execute_action("show_system_info")
print(f"Action result: {message}")
```

### Learning Visualization
```python
from visualizer import LearningVisualizer
from logger import Logger

logger = Logger()
visualizer = LearningVisualizer(logger)
plots = visualizer.create_comprehensive_report()
```

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Voice Input Not Working**: Install optional dependencies
   ```bash
   pip install SpeechRecognition pyaudio
   ```

3. **Permission Issues**: Some system actions may require elevated permissions

4. **Port Already in Use**: If Streamlit shows port conflicts, try:
   ```bash
   streamlit run streamlit_app.py --server.port 8502
   ```

### Debugging Tips

- Use VS Code's integrated debugger to step through code
- Check the `logs/` directory for detailed execution logs
- Run `python test_vscode.py` to verify all components work
- Monitor console output for detailed error messages

## 🎉 Success Indicators

You'll know everything is working when:

- ✅ `python test_vscode.py` shows "All tests passed!"
- ✅ `python demo.py` launches the interactive menu
- ✅ Tasks process successfully with reward tracking
- ✅ Q-table persistence works across sessions
- ✅ Learning curves generate correctly

## 🚀 Next Steps

1. **Explore Features**: Try different demo options
2. **Customize Tasks**: Modify `task_scenarios.py` for your needs
3. **Extend Actions**: Add new device actions in `device_actions.py`
4. **Monitor Learning**: Use the Streamlit dashboard for real-time monitoring
5. **Analyze Results**: Check generated reports in the `logs/` directory

## 📞 Support

If you encounter any issues:

1. Run the compatibility test: `python test_vscode.py`
2. Check the error logs in the `logs/` directory
3. Verify all dependencies are correctly installed
4. Ensure you're using Python 3.8+ with VS Code Python extension

---

**Ready to start learning! 🤖📚**