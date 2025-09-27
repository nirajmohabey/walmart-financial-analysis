# Walmart Financial Analysis

A comprehensive financial analysis tool for Walmart Inc. (WMT) with advanced ratio calculations, risk assessment, and interactive dashboards.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the main application
python main.py
```

## Features

- **Financial Ratios**: 30+ liquidity, leverage, profitability, and efficiency ratios
- **Risk Assessment**: Altman Z-Score and Piotroski F-Score analysis
- **Advanced Metrics**: DuPont Analysis, EVA, Free Cash Flow Yield
- **Interactive Dashboard**: Real-time visualization with Streamlit
- **Performance Optimization**: Data caching and parallel processing

## Project Structure

```
├── data/                          # Raw financial data
│   └── Financial Statements (wmt).xlsx
├── src/                           # Core modules
│   ├── core/                      # Data processing & calculations
│   │   ├── data_loader.py         # Optimized data loading with caching
│   │   └── ratio_calculator.py    # Comprehensive ratio calculations
│   └── streamlit/                 # Interactive dashboard
│       └── app.py                 # Streamlit web application
├── output/                        # Analysis results
│   ├── analysis_summary.json      # Detailed metrics in JSON
│   ├── analysis_summary.txt       # Human-readable summary
│   └── walmart_financial_ratios.csv # All calculated ratios
├── logs/                          # System logs and cache
│   ├── analysis.log              # Execution logs
│   └── data_cache.pkl            # Cached data for faster runs
├── main.py                        # Main application launcher
├── run_analysis.py                # Analysis runner
├── basic_analysis.py              # Basic analysis (fallback)
└── requirements.txt               # Python dependencies
```

## Usage

### Main Application
```bash
python main.py
```

### Direct Analysis
```bash
python run_analysis.py
```

### Interactive Dashboard
```bash
streamlit run src/streamlit/app.py
```

## Analysis Types

### 1. Financial Ratios
- **Liquidity**: Current Ratio, Quick Ratio, Cash Ratio
- **Leverage**: Debt-to-Equity, Interest Coverage, Debt Ratio
- **Profitability**: ROA, ROE, Net Margin, Gross Margin
- **Efficiency**: Asset Turnover, Inventory Turnover, Receivables Turnover

### 2. Risk Assessment
- **Altman Z-Score**: Bankruptcy prediction model
- **Piotroski F-Score**: Financial strength assessment

### 3. Advanced Analysis
- **DuPont Analysis**: ROE decomposition
- **Economic Value Added (EVA)**: Value creation measurement
- **Free Cash Flow**: Cash generation analysis

## Output Files

- **analysis_summary.txt**: Human-readable summary with key insights
- **analysis_summary.json**: Machine-readable data with all metrics
- **walmart_financial_ratios.csv**: Comprehensive spreadsheet with all ratios

## Requirements

- Python 3.7+
- pandas, numpy, matplotlib, seaborn, plotly
- streamlit (for dashboard)
- openpyxl (for Excel files)

## Installation

1. Clone/Download the project
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

---

**Ready to analyze?** Run `python main.py` to get started!