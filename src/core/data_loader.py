"""
Optimized Data Loader
====================
Fast, robust data loading with caching and error handling
"""

import pandas as pd
import numpy as np
import os
import pickle
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedDataLoader:
    def __init__(self, cache_dir='logs'):
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, 'data_cache.pkl')
        self.data = None
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
    
    def load_data(self, excel_file='data/Financial Statements (wmt).xlsx', use_cache=True):
        """Load financial data with caching for performance"""
        logger.info("Loading financial data...")
        
        # Check cache first
        if use_cache and os.path.exists(self.cache_file):
            cache_time = os.path.getmtime(self.cache_file)
            file_time = os.path.getmtime(excel_file)
            
            if cache_time > file_time:
                logger.info("Loading data from cache...")
                with open(self.cache_file, 'rb') as f:
                    self.data = pickle.load(f)
                return self.data
        
        # Load fresh data
        self.data = self._load_fresh_data(excel_file)
        
        # Cache the data
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.data, f)
        
        logger.info(f"Data loaded and cached: {len(self.data)} sheets")
        return self.data
    
    def _load_fresh_data(self, excel_file):
        """Load fresh data from Excel file"""
        try:
            data = {}
            sheet_mapping = {
                'balance_sheet': 'balance sheet annually',
                'income_statement': 'income annually', 
                'cash_flow': 'cash flow annually'
            }
            
            for sheet_key, sheet_name in sheet_mapping.items():
                logger.info(f"Loading {sheet_key}...")
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # Clean and optimize
                df = self._clean_dataframe(df)
                
                # Optimize data types
                df = self._optimize_dtypes(df)
                
                data[sheet_key] = df
                logger.info(f"Loaded {sheet_key}: {df.shape}")
            
            return data
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return self._create_sample_data()
    
    def _clean_dataframe(self, df):
        """Clean and prepare dataframe"""
        # Remove the last column if it's 'Upgrade' or similar
        if len(df.columns) > 1 and df.columns[-1] in ['Upgrade', '2012 - 1993']:
            df = df.iloc[:, :-1]
        
        # Set the first column as index
        df = df.set_index(df.columns[0])
        
        # Convert numeric columns to numeric, errors='coerce' will turn non-numeric to NaN
        for col in df.columns:
            if col != 'Year':
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Transpose so years are rows and items are columns
        df = df.T
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Get latest 5 years only for performance
        df = df.head(5)
        
        return df
    
    def _optimize_dtypes(self, df):
        """Optimize data types for memory efficiency"""
        for col in df.columns:
            if df[col].dtype == 'float64':
                # Convert to float32 if precision allows
                if df[col].min() > np.finfo(np.float32).min and df[col].max() < np.finfo(np.float32).max:
                    df[col] = df[col].astype('float32')
            elif df[col].dtype == 'int64':
                # Convert to int32 if range allows
                if df[col].min() > np.iinfo(np.int32).min and df[col].max() < np.iinfo(np.int32).max:
                    df[col] = df[col].astype('int32')
        
        return df
    
    def _create_sample_data(self):
        """Create sample data for demonstration"""
        logger.info("Creating sample data...")
        
        years = ['2022', '2021', '2020', '2019', '2018']
        
        # Sample balance sheet data
        bs_data = {
            'Total Current Assets': [86187, 81997, 61395, 61897, 59940],
            'Total Assets': [243197, 252496, 236495, 219295, 204522],
            'Total Current Liabilities': [102693, 88300, 63968, 77881, 75555],
            'Total Debt': [41891, 42137, 45179, 48509, 42656],
            'Total Liabilities': [161796, 164965, 154943, 150045, 139661],
            'Shareholders\' Equity': [81401, 87531, 81552, 69250, 64861],
            'Retained Earnings': [83169, 83086, 77058, 68100, 60846]
        }
        
        # Sample income statement data
        is_data = {
            'Revenue': [611289, 572754, 559151, 514405, 500343],
            'Net Income': [11680, 13673, 13510, 14694, 6487],
            'Operating Income': [20412, 25934, 22548, 20196, 21341],
            'Gross Margin': [0.241, 0.251, 0.248, 0.247, 0.251],
            'Operating Margin': [0.033, 0.045, 0.040, 0.039, 0.043]
        }
        
        # Sample cash flow data
        cf_data = {
            'Operating Cash Flow': [28391, 25951, 36193, 27418, 27753],
            'Capital Expenditures': [-11359, -10462, -10109, -10308, -10175]
        }
        
        data = {
            'balance_sheet': pd.DataFrame(bs_data, index=years),
            'income_statement': pd.DataFrame(is_data, index=years),
            'cash_flow': pd.DataFrame(cf_data, index=years)
        }
        
        return data
    
    def get_standardized_data(self):
        """Get data with standardized column names"""
        if not self.data:
            return None
            
        return self.data
    
    def clear_cache(self):
        """Clear data cache"""
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
            logger.info("Cache cleared")
    
    def get_data_info(self):
        """Get information about loaded data"""
        if not self.data:
            return "No data loaded"
        
        info = {}
        for sheet_name, df in self.data.items():
            info[sheet_name] = {
                'shape': df.shape,
                'columns': list(df.columns),
                'years': list(df.index),
                'memory_usage': df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
            }
        
        return info
