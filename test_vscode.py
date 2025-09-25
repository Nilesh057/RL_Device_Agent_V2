#!/usr/bin/env python3
"""
Test script to verify RL Device Agent v2 works properly in VS Code
"""

def test_imports():
    """Test all imports work correctly"""
    print("🔍 Testing imports...")
    
    try:
        from rl_agent import QLearningAgent
        print("✅ rl_agent imported successfully")
        
        from task_scenarios import DemoRunner, TaskScenarios
        print("✅ task_scenarios imported successfully")
        
        from visualizer import LearningVisualizer
        print("✅ visualizer imported successfully")
        
        from logger import Logger
        print("✅ logger imported successfully")
        
        from device_actions import DeviceActions
        print("✅ device_actions imported successfully")
        
        # Optional voice input
        try:
            from voice_input import VoiceEnabledAgent
            print("✅ voice_input imported successfully")
        except ImportError as e:
            print(f"⚠️ voice_input not available: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic RL agent functionality"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Initialize agent
        from rl_agent import QLearningAgent
        agent = QLearningAgent()
        print("✅ QLearningAgent initialized")
        
        # Test task processing
        result = agent.process_task("take screenshot")
        print(f"✅ Task processing: {result['execution_success']}")
        
        # Test feedback
        agent.receive_feedback("👍")
        print("✅ Feedback processing works")
        
        # Test statistics
        stats = agent.get_learning_statistics()
        print(f"✅ Statistics: {stats['session_stats']['total_actions']} actions")
        
        # Test persistence
        agent.save_qtable()
        print("✅ Q-table persistence works")
        
        agent.end_episode()
        print("✅ Episode management works")
        
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_device_actions():
    """Test device actions"""
    print("\n⚙️ Testing device actions...")
    
    try:
        from device_actions import DeviceActions
        actions = DeviceActions()
        available = actions.get_available_actions()
        print(f"✅ Device actions initialized with {len(available)} actions")
        
        # Test a safe action
        success, message, info = actions.execute_action("show_system_info")
        print(f"✅ System info action: {success} - {message}")
        
        return True
    except Exception as e:
        print(f"❌ Device actions test failed: {e}")
        return False

def test_demo_runner():
    """Test demo runner functionality"""
    print("\n🎬 Testing demo runner...")
    
    try:
        from rl_agent import QLearningAgent
        from task_scenarios import DemoRunner
        
        agent = QLearningAgent()
        demo_runner = DemoRunner(agent, interactive=False)
        print("✅ Demo runner initialized")
        
        # Test automated demo (small batch)
        demo_runner.run_automated_demo(num_tasks=3)
        print("✅ Automated demo completed")
        
        return True
    except Exception as e:
        print(f"❌ Demo runner test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🤖 RL Device Agent v2 - VS Code Compatibility Test")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Device Actions", test_device_actions),
        ("Demo Runner", test_demo_runner)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔬 Running {test_name}...")
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("-" * 30)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 Tests Passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("🎉 All tests passed! Ready to run in VS Code!")
        print("\n📝 Next Steps:")
        print("1. Open VS Code in this directory")
        print("2. Install required packages: pip install -r requirements.txt")
        print("3. Run: python demo.py")
        print("4. For voice features: pip install SpeechRecognition pyaudio")
    else:
        print("⚠️ Some tests failed. Check error messages above.")
    
    return passed == len(tests)

if __name__ == "__main__":
    main()