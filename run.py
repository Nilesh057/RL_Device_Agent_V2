#!/usr/bin/env python3
"""
RL Device Agent v2 - Quick Launcher

Simple launcher script for easy access to all agent features.
"""

import os
import sys
import subprocess

def main():
    print("🤖 RL Device Agent v2 - Quick Launcher")
    print("=" * 40)
    print("Choose your interface:")
    print()
    print("1. 🎬 Complete Demo (Recommended first run)")
    print("2. 💻 CLI Interface (Command line)")  
    print("3. 🌐 Web Dashboard (Browser interface)")
    print("4. 🎤 Voice Input Test")
    print("5. 📊 Generate Sample Reports")
    print("6. 🚪 Exit")
    print()
    
    while True:
        choice = input("Select option (1-6): ").strip()
        
        if choice == "1":
            print("\n🎬 Launching complete demo...")
            subprocess.run([sys.executable, "demo.py"])
            break
            
        elif choice == "2":
            print("\n💻 Launching CLI interface...")
            subprocess.run([sys.executable, "rl_agent.py"])
            break
            
        elif choice == "3":
            print("\n🌐 Launching web dashboard...")
            print("Dashboard will open at http://localhost:8501")
            subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
            break
            
        elif choice == "4":
            print("\n🎤 Testing voice input...")
            subprocess.run([sys.executable, "voice_input.py"])
            break
            
        elif choice == "5":
            print("\n📊 Generating sample reports...")
            subprocess.run([sys.executable, "task_scenarios.py"])
            break
            
        elif choice == "6":
            print("\n👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-6.")

if __name__ == "__main__":
    main()