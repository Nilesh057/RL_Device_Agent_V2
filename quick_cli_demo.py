#!/usr/bin/env python3
"""
Quick CLI Demo for RL Device Agent v2
Demonstrates basic usage without full interactive session
"""

from rl_agent import QLearningAgent
import sys
import time

def run_quick_cli_demo():
    """Run a quick demonstration of the CLI interface"""
    print("🤖 RL Device Agent v2 - Quick CLI Demo")
    print("=" * 50)
    
    try:
        # Initialize agent
        print("🔧 Initializing RL Agent...")
        agent = QLearningAgent()
        
        print(f"\n✅ Agent initialized successfully!")
        print(f"📊 Q-table contains {len(agent.q_table)} learned states")
        print(f"🎯 Available actions: {len(agent.available_actions)}")
        
        # Demonstrate a few tasks
        demo_tasks = [
            "open notepad",
            "take screenshot", 
            "mute audio"
        ]
        
        print(f"\n🎬 Running demo with {len(demo_tasks)} tasks...")
        print("-" * 30)
        
        for i, task in enumerate(demo_tasks, 1):
            print(f"\n🎯 Task {i}: '{task}'")
            
            # Process task
            result = agent.process_task(task)
            
            # Show results
            print(f"   🤖 Selected Action: {result['selected_action']}")
            print(f"   🔮 Confidence: {result['confidence_score']:.3f}")
            print(f"   ⚡ Success: {'✅' if result['execution_success'] else '❌'}")
            print(f"   💡 Next Best: {[a[0] for a in result['next_best_actions'][:2]]}")
            
            # Simulate feedback (automated for demo)
            if result['execution_success'] and result['confidence_score'] > 0.5:
                feedback = "👍"
                print(f"   💬 Feedback: {feedback} (automated)")
                agent.receive_feedback(feedback)
            else:
                feedback = "👎"
                print(f"   💬 Feedback: {feedback} (automated)")
                agent.receive_feedback(feedback, suggested_action="open_notepad")
            
            time.sleep(0.5)  # Brief pause
        
        # End episode and show stats
        agent.end_episode()
        
        # Show final statistics
        stats = agent.get_learning_statistics()
        print(f"\n📊 Final Statistics:")
        print(f"   🧠 Q-table states: {stats['qtable_stats']['total_states']}")
        print(f"   🎯 Success rate: {stats['session_stats']['success_rate']:.1%}")
        print(f"   🔮 Avg confidence: {stats['session_stats']['average_confidence']:.3f}")
        print(f"   🔍 Exploration rate: {stats['qtable_stats']['exploration_rate']:.3f}")
        
        print(f"\n✅ Demo completed successfully!")
        print(f"💾 Learning data saved to logs/ and models/")
        
        # Show how to access full CLI
        print(f"\n🚀 To access the full interactive CLI, run:")
        print(f"   python3 rl_agent.py")
        
        return True
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Demo interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        return False

if __name__ == "__main__":
    success = run_quick_cli_demo()
    sys.exit(0 if success else 1)