"""
Walmart Financial Analysis - Main Application
=============================================
Main launcher that executes the consolidated analysis from analysis folder.
"""

import sys
import os
import subprocess
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main_launcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def print_banner():
    """Print main launcher banner"""
    print("="*70)
    print(" WALMART FINANCIAL ANALYSIS SUITE - MAIN LAUNCHER ")
    print("="*70)
    print(" Launches consolidated analysis from analysis folder")
    print(f" Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

def run_analysis():
    """Run the consolidated analysis from analysis folder"""
    logger.info("Launching consolidated analysis from src/analysis/analysis.py...")
    
    try:
        # Ensure necessary directories exist
        os.makedirs('logs', exist_ok=True)
        os.makedirs('output', exist_ok=True)
        
        # Check if analysis file exists
        analysis_file = 'src/analysis/analysis.py'
        if not os.path.exists(analysis_file):
            logger.error(f"Analysis file not found: {analysis_file}")
            print(f"Error: {analysis_file} not found.")
            return False
        
        # Execute the analysis
        result = subprocess.run([sys.executable, analysis_file], check=True, capture_output=True, text=True)
        logger.info("Analysis completed successfully.")
        print(result.stdout)
        
        if result.stderr:
            logger.warning(f"Analysis stderr: {result.stderr}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Analysis failed with error: {e}")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        print(f"\nError during analysis: {e}")
        print("Check logs for details.")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        return False

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    logger.info("Launching Streamlit dashboard...")
    
    try:
        dashboard_path = "src/streamlit/app.py"
        if not os.path.exists(dashboard_path):
            logger.error(f"Dashboard file not found: {dashboard_path}")
            print(f"Error: {dashboard_path} not found.")
            return False
        
        print("\nLaunching Streamlit Dashboard...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path], check=True)
        return True
        
    except FileNotFoundError:
        logger.error("Streamlit not found. Please install: pip install streamlit")
        print("Error: Streamlit not found. Install with: pip install streamlit")
        return False
    except Exception as e:
        logger.error(f"Error launching dashboard: {e}")
        print(f"Error launching dashboard: {e}")
        return False

def main():
    """Main function - runs everything automatically"""
    print_banner()
    
    print("\nRunning Complete Financial Analysis...")
    success = run_analysis()
    
    if success:
        print("\nAnalysis completed successfully!")
        print("Check the 'output' folder for results.")
        
        print("\nLaunching Interactive Dashboard...")
        launch_dashboard()
    else:
        print("\nAnalysis failed. Check logs for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    main()