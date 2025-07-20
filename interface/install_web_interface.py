#!/usr/bin/env python3
"""
NSE Backtesting Engine Web Interface Installation Script
========================================================

This script installs the required dependencies for the web interface
and sets up the necessary directories and files.

Usage:
    python install_web_interface.py
"""

import os
import sys
import subprocess
import importlib.util

def check_python_version():
    """Check if Python version is compatible"""
    
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def install_dependencies():
    """Install required dependencies"""
    
    print("\n📦 Installing web interface dependencies...")
    
    # Required packages for web interface
    web_packages = [
        'streamlit>=1.28.0',
        'plotly>=5.17.0',
        'streamlit-ace>=0.1.1',
        'streamlit-aggrid>=0.3.4'
    ]
    
    # Check which packages are missing
    missing_packages = []
    
    for package in web_packages:
        package_name = package.split('>=')[0].split('==')[0]
        try:
            if package_name == 'streamlit-ace':
                import streamlit_ace
            elif package_name == 'streamlit-aggrid':
                import st_aggrid
            else:
                importlib.import_module(package_name)
            print(f"  ✅ {package_name}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package_name} (missing)")
    
    if not missing_packages:
        print("✅ All dependencies already installed!")
        return True
    
    print(f"\n📥 Installing {len(missing_packages)} missing packages...")
    
    # Try different installation methods
    installation_success = False
    
    # Method 1: Try uv (if available)
    try:
        print("🔄 Trying installation with uv...")
        subprocess.run(['uv', 'add'] + missing_packages, check=True, capture_output=True)
        print("✅ Successfully installed with uv!")
        installation_success = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  uv not available or failed")
    
    # Method 2: Try pip
    if not installation_success:
        try:
            print("🔄 Trying installation with pip...")
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, 
                         check=True, capture_output=True)
            print("✅ Successfully installed with pip!")
            installation_success = True
        except subprocess.CalledProcessError as e:
            print(f"❌ pip installation failed: {e}")
    
    # Method 3: Try conda (if available)
    if not installation_success:
        try:
            print("🔄 Trying installation with conda...")
            # Convert package names for conda
            conda_packages = [pkg.split('>=')[0] for pkg in missing_packages]
            subprocess.run(['conda', 'install', '-c', 'conda-forge'] + conda_packages, 
                         check=True, capture_output=True)
            print("✅ Successfully installed with conda!")
            installation_success = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  conda not available or failed")
    
    if not installation_success:
        print("❌ All installation methods failed!")
        print("\n💡 Manual installation required:")
        for package in missing_packages:
            print(f"  pip install {package}")
        return False
    
    return True

def setup_directories():
    """Create necessary directories"""
    
    print("\n📁 Setting up directories...")
    
    directories = [
        'strategies',
        'backtest_results',
        'logs',
        'temp',
        'exports'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"  ✅ Created: {directory}/")
        else:
            print(f"  ✅ Exists: {directory}/")
    
    return True

def create_sample_files():
    """Create sample configuration and strategy files"""
    
    print("\n📄 Creating sample files...")
    
    # Create .streamlit directory and config
    streamlit_dir = ".streamlit"
    if not os.path.exists(streamlit_dir):
        os.makedirs(streamlit_dir)
    
    # Streamlit config
    config_content = """[general]
developmentMode = false

[server]
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
"""
    
    config_path = os.path.join(streamlit_dir, "config.toml")
    if not os.path.exists(config_path):
        with open(config_path, 'w') as f:
            f.write(config_content)
        print(f"  ✅ Created: {config_path}")
    else:
        print(f"  ✅ Exists: {config_path}")
    
    return True

def verify_installation():
    """Verify that everything is installed correctly"""
    
    print("\n🔍 Verifying installation...")
    
    # Check core files
    required_files = [
        'web_interface.py',
        'web_config.py',
        'launch_web_interface.py'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (missing)")
            return False
    
    # Check imports
    try:
        import streamlit
        import plotly
        print("  ✅ Core web dependencies")
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    
    # Check engine components
    try:
        from engine.enhanced_zipline_runner import EnhancedZiplineRunner
        from engine.enhanced_base_strategy import BaseStrategy
        print("  ✅ Engine components")
    except ImportError as e:
        print(f"  ⚠️  Engine import warning: {e}")
        print("     (This is OK if you haven't set up the engine yet)")
    
    return True

def show_next_steps():
    """Show next steps after installation"""
    
    print("\n🎉 Installation Complete!")
    print("=" * 40)
    
    print("\n🚀 Next Steps:")
    print("1. Launch the web interface:")
    print("   python launch_web_interface.py")
    print("   OR")
    print("   streamlit run web_interface.py")
    
    print("\n2. Open your browser and go to:")
    print("   http://localhost:8501")
    
    print("\n3. Start building strategies:")
    print("   - Go to 'Strategy Builder' page")
    print("   - Choose a template or start from scratch")
    print("   - Write and test your strategies")
    
    print("\n📚 Documentation:")
    print("   - WEB_INTERFACE_README.md - Complete usage guide")
    print("   - demo_web_interface.py - Demo and examples")
    
    print("\n💡 Tips:")
    print("   - Run demo_web_interface.py for a quick demo")
    print("   - Check WEB_INTERFACE_README.md for detailed instructions")
    print("   - Use Strategy Builder templates to get started quickly")

def main():
    """Main installation function"""
    
    print("🔧 NSE Backtesting Engine Web Interface Installation")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Installation failed!")
        print("Please install dependencies manually and try again.")
        sys.exit(1)
    
    # Setup directories
    if not setup_directories():
        print("\n❌ Directory setup failed!")
        sys.exit(1)
    
    # Create sample files
    if not create_sample_files():
        print("\n❌ Sample file creation failed!")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("\n⚠️  Installation verification had issues!")
        print("The web interface may still work, but some features might be limited.")
    
    # Show next steps
    show_next_steps()
    
    # Ask if user wants to launch immediately
    try:
        response = input("\n❓ Launch web interface now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            print("\n🚀 Launching web interface...")
            subprocess.run([sys.executable, 'launch_web_interface.py'])
    except KeyboardInterrupt:
        print("\n👋 Installation completed!")

if __name__ == "__main__":
    main()
