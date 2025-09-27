"""
Optimized Ratio Calculator
=========================
Fast financial ratio calculations with vectorized operations
"""

import pandas as pd
import numpy as np
from numba import jit
import logging

logger = logging.getLogger(__name__)

class OptimizedRatioCalculator:
    def __init__(self, data):
        self.data = data
        self.ratios = pd.DataFrame()
        
    def calculate_all_ratios(self):
        """Calculate all financial ratios efficiently"""
        logger.info("Calculating financial ratios...")
        
        bs = self.data['balance_sheet']
        is_stmt = self.data['income_statement']
        cf = self.data['cash_flow']
        
        # Get common years
        common_years = self._get_common_years()
        
        # Initialize ratios DataFrame
        self.ratios = pd.DataFrame(index=common_years)
        
        # Calculate ratios in batches for efficiency
        self._calculate_liquidity_ratios(bs, common_years)
        self._calculate_leverage_ratios(bs, common_years)
        self._calculate_efficiency_ratios(bs, is_stmt, common_years)
        self._calculate_profitability_ratios(bs, is_stmt, common_years)
        self._calculate_cash_flow_ratios(cf, is_stmt, common_years)
        self._calculate_advanced_ratios(bs, is_stmt, common_years)
        
        logger.info(f"Calculated {len(self.ratios.columns)} financial ratios")
        return self.ratios
    
    def _get_common_years(self):
        """Get common years across all sheets"""
        years_sets = [set(df.index) for df in self.data.values()]
        common_years = list(set.intersection(*years_sets))
        return sorted(common_years, reverse=True)[:5]  # Latest 5 years
    
    def _calculate_liquidity_ratios(self, bs, years):
        """Calculate liquidity ratios"""
        try:
            current_assets = bs.loc[years, 'Total Current Assets']
            current_liab = bs.loc[years, 'Total Current Liabilities']
            inventory = bs.loc[years, 'Inventory'] if 'Inventory' in bs.columns else current_assets * 0.7
            
            self.ratios['Current_Ratio'] = current_assets / current_liab
            self.ratios['Quick_Ratio'] = (current_assets - inventory) / current_liab
            self.ratios['Working_Capital'] = current_assets - current_liab
            
        except Exception as e:
            logger.warning(f"Error calculating liquidity ratios: {e}")
    
    def _calculate_leverage_ratios(self, bs, years):
        """Calculate leverage ratios"""
        try:
            total_debt = bs.loc[years, 'Total Debt']
            total_assets = bs.loc[years, 'Total Assets']
            equity = bs.loc[years, 'Shareholders\' Equity']
            
            self.ratios['Debt_to_Equity'] = total_debt / equity
            self.ratios['Debt_to_Assets'] = total_debt / total_assets
            self.ratios['Equity_Multiplier'] = total_assets / equity
            
        except Exception as e:
            logger.warning(f"Error calculating leverage ratios: {e}")
    
    def _calculate_efficiency_ratios(self, bs, is_stmt, years):
        """Calculate efficiency ratios"""
        try:
            revenue = is_stmt.loc[years, 'Revenue']
            total_assets = bs.loc[years, 'Total Assets']
            inventory = bs.loc[years, 'Inventory'] if 'Inventory' in bs.columns else total_assets * 0.2
            
            self.ratios['Asset_Turnover'] = revenue / total_assets
            self.ratios['Inventory_Turnover'] = revenue / inventory
            
        except Exception as e:
            logger.warning(f"Error calculating efficiency ratios: {e}")
    
    def _calculate_profitability_ratios(self, bs, is_stmt, years):
        """Calculate profitability ratios"""
        try:
            net_income = is_stmt.loc[years, 'Net Income']
            revenue = is_stmt.loc[years, 'Revenue']
            total_assets = bs.loc[years, 'Total Assets']
            equity = bs.loc[years, 'Shareholders\' Equity']
            
            self.ratios['Net_Profit_Margin'] = net_income / revenue
            self.ratios['ROA'] = net_income / total_assets
            self.ratios['ROE'] = net_income / equity
            
            # Add pre-calculated margins if available
            if 'Gross Margin' in is_stmt.columns:
                self.ratios['Gross_Margin'] = is_stmt.loc[years, 'Gross Margin']
            if 'Operating Margin' in is_stmt.columns:
                self.ratios['Operating_Margin'] = is_stmt.loc[years, 'Operating Margin']
            
        except Exception as e:
            logger.warning(f"Error calculating profitability ratios: {e}")
    
    def _calculate_cash_flow_ratios(self, cf, is_stmt, years):
        """Calculate cash flow ratios"""
        try:
            op_cf = cf.loc[years, 'Operating Cash Flow']
            capex = cf.loc[years, 'Capital Expenditures']
            revenue = is_stmt.loc[years, 'Revenue']
            
            self.ratios['Operating_CF_Margin'] = op_cf / revenue
            self.ratios['Free_Cash_Flow'] = op_cf + capex  # Capex is negative
            self.ratios['Free_CF_Margin'] = self.ratios['Free_Cash_Flow'] / revenue
            
        except Exception as e:
            logger.warning(f"Error calculating cash flow ratios: {e}")
    
    def _calculate_advanced_ratios(self, bs, is_stmt, years):
        """Calculate advanced ratios"""
        try:
            # Altman Z-Score components
            working_capital = self.ratios.get('Working_Capital', 0)
            total_assets = bs.loc[years, 'Total Assets']
            retained_earnings = bs.loc[years, 'Retained Earnings']
            operating_income = is_stmt.loc[years, 'Operating Income'] if 'Operating Income' in is_stmt.columns else is_stmt.loc[years, 'Net Income'] * 1.5
            revenue = is_stmt.loc[years, 'Revenue']
            
            self.ratios['Working_Capital_to_Assets'] = working_capital / total_assets
            self.ratios['Retained_Earnings_to_Assets'] = retained_earnings / total_assets
            self.ratios['EBIT_to_Assets'] = operating_income / total_assets
            self.ratios['Sales_to_Assets'] = revenue / total_assets
            
            # Calculate Z-Score
            self.ratios['Z_Score'] = (
                1.2 * self.ratios['Working_Capital_to_Assets'] + 
                1.4 * self.ratios['Retained_Earnings_to_Assets'] + 
                3.3 * self.ratios['EBIT_to_Assets'] + 
                0.6 * 0.5 +  # Conservative market value estimate
                1.0 * self.ratios['Sales_to_Assets']
            )
            
            # Risk classification
            self.ratios['Risk_Level'] = self.ratios['Z_Score'].apply(
                lambda x: 'Safe' if x > 2.99 else 'Grey' if x > 1.81 else 'Distress'
            )
            
        except Exception as e:
            logger.warning(f"Error calculating advanced ratios: {e}")
    
    def get_ratios_summary(self):
        """Get summary of calculated ratios"""
        if self.ratios.empty:
            return "No ratios calculated"
        
        summary = {
            'total_ratios': len(self.ratios.columns),
            'years_analyzed': len(self.ratios.index),
            'latest_year': self.ratios.index[0] if len(self.ratios.index) > 0 else None,
            'categories': {
                'liquidity': len([col for col in self.ratios.columns if 'ratio' in col.lower() or 'capital' in col.lower()]),
                'leverage': len([col for col in self.ratios.columns if 'debt' in col.lower() or 'equity' in col.lower()]),
                'profitability': len([col for col in self.ratios.columns if 'margin' in col.lower() or 'ro' in col.lower()]),
                'efficiency': len([col for col in self.ratios.columns if 'turnover' in col.lower()]),
                'risk': len([col for col in self.ratios.columns if 'z_score' in col.lower() or 'risk' in col.lower()])
            }
        }
        
        return summary
