#!/usr/bin/env python3
"""
NSE Backtesting Engine Web Interface Launcher
==============================================

Simple launcher script for the web interface.
This script handles dependency installation and launches the Streamlit app.

Usage:
    python launch_web_interface.py
"""

import os
import sys
import subprocess
import importlib.util

def check_and_install_dependencies():
    """Check and install required dependencies"""
    
    required_packages = [
        'streamlit',
        'plotly',
        'streamlit-ace',
        'streamlit-aggrid'
    ]
    
    missing_packages = []
    
    print("🔍 Checking dependencies...")
    
    for package in required_packages:
        try:
            if package == 'streamlit-ace':
                import streamlit_ace
            elif package == 'streamlit-aggrid':
                import st_aggrid
            else:
                importlib.import_module(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package} (missing)")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        
        try:
            # Try uv first (if available)
            subprocess.run(['uv', 'add'] + missing_packages, check=True)
            print("✅ Dependencies installed successfully with uv!")
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                # Fallback to pip
                subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, check=True)
                print("✅ Dependencies installed successfully with pip!")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install dependencies: {e}")
                print("\n💡 Please install manually:")
                for package in missing_packages:
                    print(f"  pip install {package}")
                return False
    
    return True

def launch_streamlit():
    """Launch the Streamlit web interface"""
    
    print("\n🚀 Launching NSE Backtesting Engine Web Interface...")
    print("=" * 60)
    print("📱 The web interface will open in your default browser")
    print("🔗 URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            'web_interface.py',
            '--server.port=8501',
            '--server.address=localhost',
            '--browser.gatherUsageStats=false'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to launch Streamlit: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Web interface stopped by user")
        return True
    
    return True

def main():
    """Main launcher function"""
    
    print("🎯 NSE Backtesting Engine Web Interface Launcher")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('web_interface.py'):
        print("❌ Error: web_interface.py not found!")
        print("💡 Please run this script from the zipline-engine directory")
        sys.exit(1)
    
    # Check and install dependencies
    if not check_and_install_dependencies():
        print("❌ Dependency installation failed. Please install manually and try again.")
        sys.exit(1)
    
    # Launch the web interface
    if not launch_streamlit():
        print("❌ Failed to launch web interface")
        sys.exit(1)

if __name__ == "__main__":
    main()
