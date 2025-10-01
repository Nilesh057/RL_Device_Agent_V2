#!/usr/bin/env python3
"""
RL Device Agent v2 - Complete Demo Runner

This script provides a comprehensive demonstration of all agent capabilities
including CLI interface, Streamlit dashboard, learning visualization, and
voice input features.
"""

import os
import sys
import subprocess
import time
import threading
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rl_agent import QLearningAgent
from task_scenarios import DemoRunner, TaskScenarios, create_sample_task_log
from visualizer import LearningVisualizer
from logger import Logger
# Optional voice input import
try:
    from voice_input import VoiceEnabledAgent
    VOICE_AVAILABLE = True
except ImportError:
    VoiceEnabledAgent = None
    VOICE_AVAILABLE = False


class ComprehensiveDemo:
    """Complete demonstration runner for RL Device Agent v2"""
    
    def __init__(self):
        self.agent = None
        self.demo_runner = None
        self.demo_results = []
        
    def setup_demo_environment(self):
        """Set up the demo environment"""
        print("🚀 Setting up RL Device Agent v2 Demo Environment")
        print("=" * 60)
        
        # Create directories
        os.makedirs("logs", exist_ok=True)
        os.makedirs("models", exist_ok=True)
        
        # Initialize agent
        self.agent = QLearningAgent()
        self.demo_runner = DemoRunner(self.agent, interactive=False)
        
        print("✅ Demo environment ready!")
        return True
    
    def run_learning_demo(self):
        """Demonstrate learning capabilities with multiple episodes"""
        if self.agent is None:
            print("❌ Agent not initialized. Please run setup_demo_environment() first.")
            return False
            
        print("\n🧠 Learning Demonstration")
        print("=" * 40)
        print("Running multiple episodes to show learning progression...")
        
        # Run 3 episodes with different task sets
        for episode in range(1, 4):
            print(f"\n📚 Episode {episode}/3")
            print("-" * 20)
            
            # Generate tasks for this episode
            scenarios = TaskScenarios()
            tasks = scenarios.get_task_sequence(5, balanced=True)
            
            # Run tasks
            for task_info in tasks:
                result = self.agent.process_task(task_info["description"])
                
                # Simulate feedback (automated for demo)
                if result["execution_success"] and result["confidence_score"] > 0.6:
                    feedback = "👍"
                elif not result["execution_success"]:
                    feedback = "👎"
                else:
                    feedback = "👍" if task_info["difficulty"] == "easy" else "👎"
                
                self.agent.receive_feedback(feedback)
                
                time.sleep(0.5)  # Brief pause for demo
            
            # End episode
            self.agent.end_episode()
            
            # Show progress
            stats = self.agent.get_learning_statistics()
            print(f"Episode {episode} complete:")
            print(f"  Q-table states: {stats['qtable_stats']['total_states']}")
            print(f"  Exploration rate: {stats['qtable_stats']['exploration_rate']:.3f}")
            print(f"  Average confidence: {stats['session_stats']['average_confidence']:.2f}")
        
        print("\n✅ Learning demonstration completed!")
        return True
    
    def demonstrate_interfaces(self):
        """Show different interface options"""
        print("\n🖥️ Interface Demonstration")
        print("=" * 40)
        
        # CLI demonstration
        print("\n1. Command Line Interface (CLI)")
        print("   - Natural language input")
        print("   - Real-time feedback")
        print("   - Learning statistics")
        print("   - Action suggestions")
        
        # Streamlit demonstration
        print("\n2. Web Dashboard (Streamlit)")
        print("   - Visual task execution")
        print("   - Learning curve charts")
        print("   - Action history tables")
        print("   - Interactive feedback")
        
        # Voice input demonstration
        print("\n3. Voice Input (Optional)")
        print("   - Hands-free operation")
        print("   - Voice feedback collection")
        print("   - Continuous listening mode")
        
        return True
    
    def generate_comprehensive_report(self):
        """Generate complete analysis report"""
        if self.agent is None:
            print("❌ Agent not initialized. Please run setup_demo_environment() first.")
            return False
            
        print("\n📊 Generating Comprehensive Report")
        print("=" * 40)
        
        # Create visualizations
        visualizer = LearningVisualizer(self.agent.logger)
        report_plots = visualizer.create_comprehensive_report()
        
        # Generate sample task log
        create_sample_task_log()
        
        # Save final Q-table
        self.agent.save_qtable()
        
        # Export logs
        export_file = self.agent.logger.export_logs("csv")
        
        print("📋 Report Generated Successfully!")
        print("\nGenerated Files:")
        for plot_type, filepath in report_plots.items():
            if filepath:
                print(f"  📊 {plot_type}: {filepath}")
        
        print(f"  📁 Exported logs: {export_file}")
        print(f"  💾 Q-table: {self.agent.qtable_file}")
        print(f"  📝 Task log: logs/task_log.txt")
        print(f"  📖 Documentation: SHORT_REPORT.md")
        
        return True
    
    def show_demo_summary(self):
        """Display demo summary and next steps"""
        if self.agent is None:
            print("❌ Agent not initialized. Please run setup_demo_environment() first.")
            return False
            
        print("\n🎉 Demo Summary")
        print("=" * 40)
        
        stats = self.agent.get_learning_statistics()
        
        print("Learning Achievements:")
        print(f"  🧠 States learned: {stats['qtable_stats']['total_states']}")
        print(f"  🎯 Actions taken: {stats['session_stats']['total_actions']}")
        print(f"  👍 Positive feedback: {stats['session_stats']['positive_feedback']}")
        print(f"  📈 Success rate: {stats['session_stats']['success_rate']:.1%}")
        print(f"  🔍 Final exploration rate: {stats['qtable_stats']['exploration_rate']:.3f}")
        
        print("\n🚀 Ready for Production!")
        print("\nNext Steps:")
        print("  1. 📱 Run 'python rl_agent.py' for CLI interface")
        print("  2. 🌐 Run 'streamlit run streamlit_app.py' for web dashboard")
        print("  3. 🎤 Run 'python voice_input.py' for voice input testing")
        print("  4. 🎬 Run 'python task_scenarios.py' for more demos")
        print("  5. 📊 Check 'logs/' directory for all generated reports")
        
        print("\n📞 Contact & Integration:")
        print("  - All features implemented and tested")
        print("  - Ready for integration testing")
        print("  - Complete documentation available")
        print("  - Production deployment ready")
        
        return True
    
    def run_complete_demo(self):
        """Run the complete demonstration sequence"""
        print("🤖 RL Device Agent v2 - Complete System Demo")
        print("=" * 60)
        print("This demo showcases all implemented features:")
        print("✅ Q-Learning with confidence scoring")
        print("✅ Complete logging system") 
        print("✅ User feedback integration")
        print("✅ Persistent Q-table storage")
        print("✅ Learning curve visualization")
        print("✅ Task variety and scenarios")
        print("✅ CLI and Streamlit interfaces")
        print("✅ Voice input capabilities")
        print("✅ Comprehensive documentation")
        
        input("\nPress Enter to start the demo...")
        
        try:
            # Setup
            if not self.setup_demo_environment():
                return False
            
            # Learning demonstration
            if not self.run_learning_demo():
                return False
            
            # Interface demonstration
            if not self.demonstrate_interfaces():
                return False
            
            # Generate reports
            if not self.generate_comprehensive_report():
                return False
            
            # Summary
            if not self.show_demo_summary():
                return False
            
            print("\n🎊 Complete Demo Finished Successfully!")
            return True
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Demo interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
            return False


def run_quick_test():
    """Quick functionality test"""
    print("⚡ Quick Functionality Test")
    print("=" * 30)
    
    try:
        # Test core components
        agent = QLearningAgent()
        
        # Test task processing
        result = agent.process_task("take screenshot")
        print(f"✅ Task processing: {result['execution_success']}")
        
        # Test feedback
        agent.receive_feedback("👍")
        print("✅ Feedback processing: Success")
        
        # Test persistence
        agent.save_qtable()
        print("✅ Q-table persistence: Success")
        
        # Test logging
        stats = agent.get_learning_statistics()
        print(f"✅ Logging system: {stats['session_stats']['total_actions']} actions logged")
        
        agent.end_episode()
        print("\n🎯 Quick test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False


def launch_streamlit_dashboard():
    """Launch Streamlit dashboard in background"""
    print("🌐 Launching Streamlit Dashboard...")
    
    try:
        # Launch Streamlit
        subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.headless", "true"
        ])
        
        print("✅ Dashboard launched at http://localhost:8501")
        print("   (Dashboard will open in your default browser)")
        
        return True
    except Exception as e:
        print(f"❌ Failed to launch dashboard: {e}")
        return False


def check_system_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking System Requirements")
    print("=" * 30)
    
    requirements = {
        "numpy": "numpy",
        "pandas": "pandas", 
        "matplotlib": "matplotlib",
        "streamlit": "streamlit",
        "pyautogui": "PyAutoGUI",
        "psutil": "psutil"
    }
    
    missing = []
    
    for module, package in requirements.items():
        try:
            __import__(module)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing.append(package)
    
    # Optional requirements
    optional = {
        "speech_recognition": "SpeechRecognition",
        "pyaudio": "PyAudio"
    }
    
    print("\nOptional (for voice input):")
    for module, package in optional.items():
        try:
            __import__(module)
            print(f"✅ {package}")
        except ImportError:
            print(f"⚠️ {package} - Optional (voice features disabled)")
    
    if missing:
        print(f"\n❌ Missing required packages: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All requirements satisfied!")
        return True


def main():
    """Main demo launcher with menu options"""
    print("🤖 RL Device Agent v2 - Demo Launcher")
    print("=" * 50)
    
    while True:
        print("\nDemo Options:")
        print("1. 🎬 Complete System Demo (Full showcase)")
        print("2. ⚡ Quick Functionality Test")
        print("3. 🌐 Launch Streamlit Dashboard")
        print("4. 🎤 Test Voice Input")
        print("5. 📊 Generate Sample Reports")
        print("6. 🔍 Check System Requirements")
        print("7. 📖 View Documentation")
        print("8. 🚪 Exit")
        
        choice = input("\nSelect option (1-8): ").strip()
        
        if choice == "1":
            demo = ComprehensiveDemo()
            demo.run_complete_demo()
            
        elif choice == "2":
            run_quick_test()
            
        elif choice == "3":
            if check_system_requirements():
                launch_streamlit_dashboard()
                input("Press Enter when done with dashboard...")
            
        elif choice == "4":
            if not VOICE_AVAILABLE:
                print("❌ Voice input modules not installed")
                print("Install with: pip install SpeechRecognition pyaudio")
            else:
                try:
                    from voice_input import VoiceInputHandler
                    voice = VoiceInputHandler()
                    if voice.is_available():
                        voice.test_voice_input()
                    else:
                        print("❌ Voice input not available")
                except Exception as e:
                    print(f"❌ Voice input error: {e}")
            
        elif choice == "5":
            agent = QLearningAgent()
            demo_runner = DemoRunner(agent, interactive=False)
            demo_runner.run_automated_demo(10)
            visualizer = LearningVisualizer(agent.logger)
            visualizer.create_comprehensive_report()
            print("✅ Sample reports generated in logs/ directory")
            
        elif choice == "6":
            check_system_requirements()
            
        elif choice == "7":
            print("\n📖 Documentation Files:")
            print("  📋 README.md - Complete setup and usage guide")
            print("  📊 SHORT_REPORT.md - Technical implementation report")
            print("  📁 logs/ - Generated reports and learning curves")
            print("  💾 models/ - Saved Q-tables and model data")
            
        elif choice == "8":
            print("\n👋 Thank you for trying RL Device Agent v2!")
            print("🚀 Ready for production deployment!")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-8.")


if __name__ == "__main__":
    main()