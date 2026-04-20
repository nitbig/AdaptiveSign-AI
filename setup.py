#!/usr/bin/env python
"""
🔧 SETUP SCRIPT - ANNI MODERN STREAMLIT UI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Automated setup for the Agentic AI Hindsight Learning System
Installs dependencies and prepares the environment
"""

import subprocess
import sys
import os
from pathlib import Path


def print_header():
    """Print welcome header"""
    print("\n" + "=" * 70)
    print("   🔧 ANNI SETUP - AGENTIC AI HINDSIGHT LEARNING SYSTEM")
    print("=" * 70 + "\n")


def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        print(f"   Current: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def install_dependencies():
    """Install required packages"""
    print("\n📦 Installing dependencies...")
    print("   This may take a few minutes...\n")
    
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("   Try manually: pip install -r requirements.txt")
        return False


def check_models():
    """Check for required model files"""
    print("\n🤖 Checking model files...")
    
    models = {
        'hand_landmarker.task': 'Hand Tracking Model',
    }
    
    all_ok = True
    for filename, name in models.items():
        if Path(filename).exists():
            print(f"   ✅ {name}")
        else:
            print(f"   ⚠️  {name} - {filename} (will be created on first use)")
            all_ok = False
    
    return all_ok


def check_camera():
    """Check if camera is available"""
    print("\n📹 Checking camera...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("   ✅ Camera detected")
            cap.release()
            return True
        else:
            print("   ⚠️  Camera not found")
            print("      (You can still test without camera)")
            return True
    except Exception as e:
        print(f"   ⚠️  Camera check failed: {e}")
        return True


def create_memory_file():
    """Create empty memory file if not exists"""
    if not Path("hindsight_memory.json").exists():
        with open("hindsight_memory.json", "w") as f:
            f.write("{}")
        print("✅ Created memory file")
        return True
    return False


def show_next_steps():
    """Show next steps"""
    print("\n" + "=" * 70)
    print("   ✅ SETUP COMPLETE!")
    print("=" * 70)
    
    print("\n🚀 TO START THE UI:\n")
    print("   python run_streamlit_ui.py")
    
    print("\n🌐 Then open in browser:")
    print("   http://localhost:8501")
    
    print("\n📖 For detailed guide, see:")
    print("   STREAMLIT_UI_GUIDE.md")
    
    print("\n💡 Quick Features:")
    print("   • No terminal input needed")
    print("   • Modern neon design")
    print("   • Real-time camera feed")
    print("   • AI learning system")
    print("   • Audio feedback")
    print("   • Chat interface")
    
    print("\n")


def main():
    """Main setup routine"""
    print_header()
    
    # Check Python
    if not check_python():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n⚠️  Setup incomplete - some features may not work")
        print("   Try installing manually: pip install -r requirements.txt")
    
    # Check models
    check_models()
    
    # Check camera
    check_camera()
    
    # Create memory file
    create_memory_file()
    
    # Show next steps
    show_next_steps()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        sys.exit(1)
