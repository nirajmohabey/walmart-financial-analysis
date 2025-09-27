"""
Walmart Financial Analysis - Complete Analysis Suite
Consolidated analysis file containing all financial calculations and analysis
"""
import pandas as pd
import numpy as np
import os
import logging
import pickle
import json
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.data_loader import OptimizedDataLoader
from src.core.ratio_calculator import OptimizedRatioCalculator

# Setup logging
log_file = os.path.join(os.path.dirname(__file__), '..', '..', 'logs', 'analysis.log')
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WalmartFinancialAnalysis:
    """
    Complete Walmart Financial Analysis Suite
    Consolidates all analysis functionality into a single class
    """
    
    def __init__(self, data_file='data/Financial Statements (wmt).xlsx'):
        """Initialize the analysis suite"""
        self.data_file = data_file
        self.data_loader = OptimizedDataLoader(cache_dir='logs')
        self.ratio_calculator = None
        self.financial_data = {}
        self.ratios = pd.DataFrame()
        
    def load_data(self):
        """Load financial data from Excel file"""
        logger.info("Loading financial data...")
        try:
            self.financial_data = self.data_loader.load_data(self.data_file)
            logger.info("Financial data loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False
    
    def calculate_ratios(self):
        """Calculate all financial ratios"""
        logger.info("Calculating financial ratios...")
        try:
            self.ratio_calculator = OptimizedRatioCalculator(self.financial_data)
            self.ratios = self.ratio_calculator.calculate_all_ratios()
            logger.info("Financial ratios calculated successfully")
            return True
        except Exception as e:
            logger.error(f"Error calculating ratios: {e}")
            return False
    
    def generate_summary(self):
        """Generate comprehensive analysis summary"""
        if self.ratios.empty:
            logger.warning("No ratios available for summary generation")
            return None
            
        try:
            latest_year = self.ratios.index.max()
            latest_ratios = self.ratios.loc[latest_year]
            
            summary = {
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_period': f"{self.ratios.index.min()} - {self.ratios.index.max()}",
                'total_ratios': len(self.ratios.columns),
                'latest_year': int(latest_year),
                'key_metrics': {
                    'current_ratio': float(latest_ratios.get('Current_Ratio', 0)),
                    'debt_to_equity': float(latest_ratios.get('Debt_to_Equity_Ratio', 0)),
                    'net_profit_margin': float(latest_ratios.get('Net_Profit_Margin', 0)),
                    'roe': float(latest_ratios.get('ROE', 0)),
                    'altman_z_score': float(latest_ratios.get('Z_Score', 0)),
                    'piotroski_f_score': float(latest_ratios.get('F_Score', 0))
                },
                'risk_assessment': {
                    'altman_risk_level': latest_ratios.get('Risk_Level', 'Unknown'),
                    'piotroski_quality': latest_ratios.get('Quality_Level', 'Unknown')
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None
    
    def save_results(self, output_dir='output'):
        """Save all analysis results to output directory"""
        logger.info("Saving analysis results...")
        
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Save ratios to CSV
            ratios_path = os.path.join(output_dir, 'walmart_financial_ratios.csv')
            self.ratios.to_csv(ratios_path)
            logger.info(f"Ratios saved to {ratios_path}")
            
            # Generate and save summary
            summary = self.generate_summary()
            if summary:
                # Save JSON summary
                json_path = os.path.join(output_dir, 'analysis_summary.json')
                with open(json_path, 'w') as f:
                    json.dump(summary, f, indent=4)
                logger.info(f"JSON summary saved to {json_path}")
                
                # Save text summary
                txt_path = os.path.join(output_dir, 'analysis_summary.txt')
                self._save_text_summary(summary, txt_path)
                logger.info(f"Text summary saved to {txt_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return False
    
    def _save_text_summary(self, summary, file_path):
        """Save human-readable text summary"""
        with open(file_path, 'w') as f:
            f.write("WALMART FINANCIAL ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {summary['analysis_date']}\n")
            f.write(f"Data Period: {summary['data_period']}\n")
            f.write(f"Latest Year: {summary['latest_year']}\n\n")
            
            f.write("KEY FINANCIAL METRICS\n")
            f.write("-" * 30 + "\n")
            metrics = summary['key_metrics']
            f.write(f"Current Ratio: {metrics['current_ratio']:.2f}\n")
            f.write(f"Debt-to-Equity: {metrics['debt_to_equity']:.2f}\n")
            f.write(f"Net Profit Margin: {metrics['net_profit_margin']:.2%}\n")
            f.write(f"Return on Equity: {metrics['roe']:.2%}\n")
            f.write(f"Altman Z-Score: {metrics['altman_z_score']:.2f}\n")
            f.write(f"Piotroski F-Score: {metrics['piotroski_f_score']:.0f}\n\n")
            
            f.write("RISK ASSESSMENT\n")
            f.write("-" * 30 + "\n")
            f.write(f"Altman Risk Level: {summary['risk_assessment']['altman_risk_level']}\n")
            f.write(f"Piotroski Quality: {summary['risk_assessment']['piotroski_quality']}\n\n")
            
            f.write("ANALYSIS COMPLETE\n")
            f.write("=" * 50 + "\n")
    
    def run_complete_analysis(self):
        """Run the complete financial analysis workflow"""
        logger.info("Starting complete Walmart financial analysis...")
        start_time = datetime.now()
        
        try:
            # Step 1: Load data
            if not self.load_data():
                return False
            
            # Step 2: Calculate ratios
            if not self.calculate_ratios():
                return False
            
            # Step 3: Save results
            if not self.save_results():
                return False
            
            # Step 4: Generate success summary
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            logger.info(f"Analysis completed successfully in {execution_time:.2f} seconds")
            self._print_success_summary()
            
            return True
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return False
    
    def _print_success_summary(self):
        """Print success summary to console"""
        print("\n" + "=" * 60)
        print("WALMART FINANCIAL ANALYSIS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Years Analyzed: {self.ratios.index.min()} - {self.ratios.index.max()}")
        print(f"Total Ratios: {len(self.ratios.columns)}")
        print(f"Output Files: 3 (CSV, JSON, TXT)")
        print("\nNEXT STEPS:")
        print("-" * 20)
        print("1. View Dashboard: streamlit run ../streamlit/app.py")
        print("2. Check Results: ../../output/analysis_summary.txt")
        print("3. Review Ratios: ../../output/walmart_financial_ratios.csv")
        print("=" * 60)
    
    def get_financial_data(self):
        """Get loaded financial data"""
        return self.financial_data
    
    def get_ratios(self):
        """Get calculated ratios"""
        return self.ratios
    
    def get_ratio_calculator(self):
        """Get ratio calculator instance"""
        return self.ratio_calculator

def main():
    """Main function to run the analysis"""
    print("Walmart Financial Analysis - Complete Suite")
    print("=" * 50)
    
    # Initialize analysis
    analysis = WalmartFinancialAnalysis()
    
    # Run complete analysis
    success = analysis.run_complete_analysis()
    
    if success:
        print("\nAnalysis completed successfully!")
        print("Check the ../../output/ folder for results.")
    else:
        print("\nAnalysis failed. Check logs for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
