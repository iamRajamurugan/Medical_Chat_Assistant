#!/usr/bin/env python3
"""
Medical Assistant - Central Entry Point
A comprehensive medical assistant chatbot with Gemini AI and Supabase backend
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_requirements():
    """Check if required packages are installed"""
    required_packages = {
        'streamlit': 'streamlit',
        'google-generativeai': 'google.generativeai',
        'supabase': 'supabase',
        'python-dotenv': 'dotenv'
    }
    
    missing_packages = []
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print(f"\nPlease install them using:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_environment():
    """Check if environment variables are set"""
    env_file = project_root / '.env'
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please create a .env file with the following variables:")
        print("GEMINI_API_KEY=your_gemini_api_key_here")
        print("SUPABASE_URL=your_supabase_url_here")
        print("SUPABASE_KEY=your_supabase_anon_key_here")
        print("\n📖 See SETUP.md for detailed instructions")
        return False
    
    # Check for placeholder values
    try:
        sys.path.insert(0, str(project_root / 'src'))
        from config import Config
        Config.validate_config()
        print("✅ Environment configuration is valid")
        return True
    except ValueError as e:
        print("❌ Environment configuration error:")
        print(str(e))
        print("\n📖 See SETUP.md for detailed setup instructions")
        print("\n🔗 Quick links:")
        print("   • Gemini API: https://makersuite.google.com/app/apikey")
        print("   • Supabase: https://supabase.com")
        return False
    except Exception as e:
        print(f"❌ Error checking environment: {e}")
        return False

def run_medical_assistant():
    """Run the medical assistant application"""
    print("🏥 Medical Assistant")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        return
    
    # Check environment
    if not check_environment():
        return
    
    print("✅ All requirements satisfied")
    print("🚀 Starting Medical Assistant...")
    print("📱 Frontend will be available at: http://localhost:8501")
    print("⚠️  Press Ctrl+C to stop the application")
    print("=" * 50)
    
    try:
        # Run Streamlit app
        streamlit_script = project_root / 'streamlit_app.py'
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(streamlit_script),
            "--server.port=8501",
            "--server.headless=true"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Medical Assistant...")
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install it:")
        print("pip install streamlit")
    except Exception as e:
        print(f"❌ Error running application: {e}")

if __name__ == "__main__":
    run_medical_assistant()