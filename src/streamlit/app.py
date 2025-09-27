"""
Walmart Financial Analysis Streamlit App
========================================
Complete interactive dashboard with all analysis features
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.analysis.analysis import WalmartFinancialAnalysis

# Page configuration
st.set_page_config(
    page_title="Walmart Financial Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache financial data"""
    try:
        analysis = WalmartFinancialAnalysis('data/Financial Statements (wmt).xlsx')
        analysis.load_data()
        analysis.calculate_ratios()
        return analysis.get_financial_data(), analysis.get_ratios()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

def create_metrics_row(ratios, financial_data):
    """Create dynamic metrics row with real-time calculations"""
    if ratios.empty:
        return
    
    latest_year = ratios.index.max()
    latest_ratios = ratios.loc[latest_year]
    
    # Calculate dynamic deltas
    revenue_data = financial_data['income_statement']['Revenue']
    revenue_delta = ((revenue_data.iloc[0] - revenue_data.iloc[1]) / revenue_data.iloc[1]) * 100
    
    net_income_data = financial_data['income_statement']['Net Income']
    net_income_delta = ((net_income_data.iloc[0] - net_income_data.iloc[1]) / net_income_data.iloc[1]) * 100
    
    
    current_ratio_delta = latest_ratios.get('Current_Ratio', 0) - ratios.iloc[1].get('Current_Ratio', 0)
    roe_delta = latest_ratios.get('ROE', 0) - ratios.iloc[1].get('ROE', 0)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Check if data is already in millions or billions
        revenue_raw = revenue_data.iloc[0]
        delta_color = "normal" if revenue_delta > 0 else "inverse"
        if revenue_raw > 1e9:  # If in billions
            revenue = revenue_raw / 1e9
            st.metric("Revenue (Latest)", f"${revenue:.1f}B", 
                     delta=f"{revenue_delta:+.1f}%", delta_color=delta_color)
        elif revenue_raw > 1e6:  # If in millions
            revenue = revenue_raw / 1e6
            st.metric("Revenue (Latest)", f"${revenue:.0f}M", 
                     delta=f"{revenue_delta:+.1f}%", delta_color=delta_color)
        else:  # Raw value
            st.metric("Revenue (Latest)", f"${revenue_raw:,.0f}", 
                     delta=f"{revenue_delta:+.1f}%", delta_color=delta_color)
    
    with col2:
        # Check if data is already in millions or billions
        net_income_raw = net_income_data.iloc[0]
        delta_color = "normal" if net_income_delta > 0 else "inverse"
        if net_income_raw > 1e9:  # If in billions
            net_income = net_income_raw / 1e9
            st.metric("Net Income (Latest)", f"${net_income:.1f}B", 
                     delta=f"{net_income_delta:+.1f}%", delta_color=delta_color)
        elif net_income_raw > 1e6:  # If in millions
            net_income = net_income_raw / 1e6
            st.metric("Net Income (Latest)", f"${net_income:.1f}M", 
                     delta=f"{net_income_delta:+.1f}%", delta_color=delta_color)
        else:  # Raw value
            st.metric("Net Income (Latest)", f"${net_income_raw:,.0f}", 
                     delta=f"{net_income_delta:+.1f}%", delta_color=delta_color)
    
    with col3:
        current_ratio = latest_ratios.get('Current_Ratio', 0)
        delta_color = "normal" if current_ratio_delta > 0 else "inverse"
        st.metric("Current Ratio", f"{current_ratio:.2f}", 
                 delta=f"{current_ratio_delta:+.2f}", delta_color=delta_color)
    
    with col4:
        roe = latest_ratios.get('ROE', 0)
        delta_color = "normal" if roe_delta > 0 else "inverse"
        st.metric("ROE", f"{roe:.2%}", 
                 delta=f"{roe_delta:+.2%}", delta_color=delta_color)

def create_liquidity_analysis(ratios):
    """Create liquidity ratios analysis with detailed explanations"""
    st.markdown('<h2 class="section-header">Liquidity Analysis</h2>', unsafe_allow_html=True)
    
    # Explanation section
    st.markdown("""
    ### 📊 What This Analysis Shows
    **Liquidity ratios measure Walmart's ability to pay short-term obligations with current assets.** 
    
    - **Current Ratio**: Current Assets ÷ Current Liabilities (ideal: >1.0)
    - **Quick Ratio**: (Current Assets - Inventory) ÷ Current Liabilities (ideal: >0.5)  
    - **Cash Ratio**: Cash ÷ Current Liabilities (most conservative measure)
    
    **Why This Matters**: Poor liquidity can force emergency borrowing, asset sales, or missed payments.
    """)
    
    liquidity_ratios = ['Current_Ratio', 'Quick_Ratio', 'Cash_Ratio']
    available_ratios = [ratio for ratio in liquidity_ratios if ratio in ratios.columns]
    
    if available_ratios:
        fig = px.line(ratios[available_ratios], 
                      title="Liquidity Ratios Over Time",
                      labels={'index': 'Year', 'value': 'Ratio'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Latest values with interpretations
        latest_values = ratios[available_ratios].iloc[-1]
        st.subheader("Current Liquidity Position")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.dataframe(latest_values.to_frame('Latest Values'))
        
        with col2:
            st.markdown("### 💡 Key Insights:")
            
            current_ratio = latest_values.get('Current_Ratio', 0)
            if current_ratio > 1.0:
                st.success(f"✅ **Current Ratio {current_ratio:.2f}**: Strong liquidity - can cover all short-term debts")
            else:
                st.error(f"❌ **Current Ratio {current_ratio:.2f}**: Liquidity concern - may struggle with short-term obligations")
            
            quick_ratio = latest_values.get('Quick_Ratio', 0)
            if quick_ratio > 0.5:
                st.info(f"📊 **Quick Ratio {quick_ratio:.2f}**: Good ability to pay debts without selling inventory")
            else:
                st.warning(f"⚠️ **Quick Ratio {quick_ratio:.2f}**: Limited ability to pay debts without inventory sales")
            
            # Trend analysis
            if len(ratios) > 1:
                current_trend = ratios['Current_Ratio'].iloc[0] - ratios['Current_Ratio'].iloc[-1]
                if current_trend > 0:
                    st.success(f"📈 **Trend**: Liquidity improving by {current_trend:.2f} over 5 years")
                else:
                    st.warning(f"📉 **Trend**: Liquidity declining by {abs(current_trend):.2f} over 5 years")

def create_profitability_analysis(ratios):
    """Create profitability analysis with detailed explanations"""
    st.markdown('<h2 class="section-header">Profitability Analysis</h2>', unsafe_allow_html=True)
    
    # Explanation section
    st.markdown("""
    ### 💰 What This Analysis Shows
    **Profitability ratios measure how effectively Walmart generates profits from operations and assets.**
    
    - **ROA (Return on Assets)**: Net Income ÷ Total Assets (how efficiently assets generate profit)
    - **ROE (Return on Equity)**: Net Income ÷ Shareholders' Equity (how effectively equity generates returns)
    - **Net Profit Margin**: Net Income ÷ Revenue (profit per dollar of sales)
    - **Gross Profit Margin**: (Revenue - COGS) ÷ Revenue (profitability after direct costs)
    
    **Why This Matters**: Higher profitability means better operational efficiency and shareholder returns.
    """)
    
    profitability_ratios = ['ROA', 'ROE', 'Net_Profit_Margin', 'Gross_Profit_Margin']
    available_ratios = [ratio for ratio in profitability_ratios if ratio in ratios.columns]
    
    if available_ratios:
        fig = px.line(ratios[available_ratios], 
                      title="Profitability Ratios Over Time",
                      labels={'index': 'Year', 'value': 'Ratio'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed insights
        latest_values = ratios[available_ratios].iloc[-1]
        
        st.subheader("Profitability Assessment")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.dataframe(latest_values.to_frame('Latest Values'))
        
        with col2:
            st.markdown("### 💡 Key Insights:")
            
            roa = latest_values.get('ROA', 0)
            if roa > 0.05:
                st.success(f"✅ **ROA {roa:.2%}**: Excellent asset efficiency - generating strong returns")
            elif roa > 0.03:
                st.info(f"📊 **ROA {roa:.2%}**: Good asset efficiency - above industry average")
            else:
                st.warning(f"⚠️ **ROA {roa:.2%}**: Below average - assets not generating optimal returns")
            
            roe = latest_values.get('ROE', 0)
            if roe > 0.15:
                st.success(f"✅ **ROE {roe:.2%}**: Outstanding shareholder returns")
            elif roe > 0.10:
                st.info(f"📊 **ROE {roe:.2%}**: Strong shareholder returns")
            else:
                st.warning(f"⚠️ **ROE {roe:.2%}**: Below average shareholder returns")
            
            net_margin = latest_values.get('Net_Profit_Margin', 0)
            if net_margin > 0.05:
                st.success(f"✅ **Net Margin {net_margin:.2%}**: Excellent profitability per sale")
            elif net_margin > 0.03:
                st.info(f"📊 **Net Margin {net_margin:.2%}**: Good profitability per sale")
            else:
                st.warning(f"⚠️ **Net Margin {net_margin:.2%}**: Thin margins - efficiency improvements needed")
            
            # Trend analysis
            if len(ratios) > 1:
                roe_trend = ratios['ROE'].iloc[0] - ratios['ROE'].iloc[-1]
                if roe_trend > 0:
                    st.success(f"📈 **ROE Trend**: Improving by {roe_trend:.2%} over 5 years")
                else:
                    st.warning(f"📉 **ROE Trend**: Declining by {abs(roe_trend):.2%} over 5 years")

def create_leverage_analysis(ratios):
    """Create leverage analysis with detailed explanations"""
    st.markdown('<h2 class="section-header">Leverage Analysis</h2>', unsafe_allow_html=True)
    
    # Explanation section
    st.markdown("""
    ### ⚖️ What This Analysis Shows
    **Leverage ratios measure Walmart's use of debt financing and ability to service debt obligations.**
    
    - **Debt-to-Equity**: Total Debt ÷ Shareholders' Equity (how much debt vs. equity financing)
    - **Debt Ratio**: Total Debt ÷ Total Assets (what portion of assets is financed by debt)
    - **Interest Coverage**: EBIT ÷ Interest Expense (ability to pay interest from operating income)
    
    **Why This Matters**: Too much debt increases bankruptcy risk, but some debt can enhance returns.
    """)
    
    leverage_ratios = ['Debt_to_Equity', 'Debt_Ratio', 'Interest_Coverage']
    available_ratios = [ratio for ratio in leverage_ratios if ratio in ratios.columns]
    
    if available_ratios:
        fig = px.line(ratios[available_ratios], 
                      title="Leverage Ratios Over Time",
                      labels={'index': 'Year', 'value': 'Ratio'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed insights
        latest_values = ratios[available_ratios].iloc[-1]
        
        st.subheader("Leverage Assessment")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.dataframe(latest_values.to_frame('Latest Values'))
        
        with col2:
            st.markdown("### 💡 Key Insights:")
            
            debt_to_equity = latest_values.get('Debt_to_Equity', 0)
            if debt_to_equity < 0.5:
                st.success(f"✅ **D/E {debt_to_equity:.2f}**: Conservative leverage - low financial risk")
            elif debt_to_equity < 1.0:
                st.info(f"📊 **D/E {debt_to_equity:.2f}**: Moderate leverage - balanced risk/return")
            elif debt_to_equity < 1.5:
                st.warning(f"⚠️ **D/E {debt_to_equity:.2f}**: High leverage - increased financial risk")
            else:
                st.error(f"🚨 **D/E {debt_to_equity:.2f}**: Very high leverage - significant risk")
            
            debt_ratio = latest_values.get('Debt_Ratio', 0)
            if debt_ratio < 0.3:
                st.success(f"✅ **Debt Ratio {debt_ratio:.2%}**: Low debt burden - strong balance sheet")
            elif debt_ratio < 0.5:
                st.info(f"📊 **Debt Ratio {debt_ratio:.2%}**: Moderate debt burden - manageable")
            else:
                st.warning(f"⚠️ **Debt Ratio {debt_ratio:.2%}**: High debt burden - monitor closely")
            
            # Interest coverage analysis
            interest_coverage = latest_values.get('Interest_Coverage', 0)
            if interest_coverage > 5:
                st.success(f"✅ **Interest Coverage {interest_coverage:.1f}x**: Excellent ability to service debt")
            elif interest_coverage > 2.5:
                st.info(f"📊 **Interest Coverage {interest_coverage:.1f}x**: Good ability to service debt")
            elif interest_coverage > 1:
                st.warning(f"⚠️ **Interest Coverage {interest_coverage:.1f}x**: Marginal ability to service debt")
            else:
                st.error(f"🚨 **Interest Coverage {interest_coverage:.1f}x**: Cannot cover interest payments")
            
            # Risk assessment
            st.markdown("### 🛡️ Risk Assessment:")
            if debt_to_equity < 1.0 and interest_coverage > 2.5:
                st.success("**Overall**: Low financial risk - healthy leverage position")
            elif debt_to_equity < 1.5 and interest_coverage > 1.5:
                st.info("**Overall**: Moderate financial risk - manageable leverage")
            else:
                st.warning("**Overall**: High financial risk - leverage levels need attention")

def create_efficiency_analysis(ratios):
    """Create efficiency analysis with detailed explanations"""
    st.markdown('<h2 class="section-header">Efficiency Analysis</h2>', unsafe_allow_html=True)
    
    # Explanation section
    st.markdown("""
    ### ⚡ What This Analysis Shows
    **Efficiency ratios measure how effectively Walmart uses its assets and manages operations.**
    
    - **Asset Turnover**: Revenue ÷ Total Assets (how much revenue generated per dollar of assets)
    - **Inventory Turnover**: COGS ÷ Average Inventory (how quickly inventory is sold)
    - **Receivables Turnover**: Revenue ÷ Average Receivables (how quickly customers pay)
    
    **Why This Matters**: Higher efficiency means better asset utilization and operational performance.
    """)
    
    efficiency_ratios = ['Asset_Turnover', 'Inventory_Turnover', 'Receivables_Turnover']
    available_ratios = [ratio for ratio in efficiency_ratios if ratio in ratios.columns]
    
    if available_ratios:
        fig = px.line(ratios[available_ratios], 
                      title="Efficiency Ratios Over Time - Higher is Better",
                      labels={'index': 'Year', 'value': 'Turnover Ratio'})
        
        # Add contextual description to the chart
        fig.update_layout(
            title_x=0.5,
            annotations=[
                dict(
                    x=0.5, y=1.15,
                    xref="paper", yref="paper",
                    text="📈 Rising lines indicate improving efficiency - more revenue/assets generated",
                    showarrow=False,
                    font=dict(size=12, color="gray")
                )
            ]
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed insights
        latest_values = ratios[available_ratios].iloc[-1]
        
        st.subheader("Efficiency Assessment")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.dataframe(latest_values.to_frame('Latest Values'))
        
        with col2:
            st.markdown("### 💡 Key Insights:")
            
            asset_turnover = latest_values.get('Asset_Turnover', 0)
            # Dynamic efficiency analysis based on actual data trends
            asset_turnover = latest_values.get('Asset_Turnover', 0)
            inventory_turnover = latest_values.get('Inventory_Turnover', 0)
            
            # Asset Turnover Analysis
            if len(ratios) > 1:
                asset_trend = ratios['Asset_Turnover'].iloc[-1] - ratios['Asset_Turnover'].iloc[-2]
                asset_avg = ratios['Asset_Turnover'].mean()
                
                if asset_turnover > asset_avg:
                    st.success(f"✅ **Asset Turnover {asset_turnover:.2f}**: Above 5-year average ({asset_avg:.2f})")
                else:
                    st.warning(f"⚠️ **Asset Turnover {asset_turnover:.2f}**: Below 5-year average ({asset_avg:.2f})")
                
                if asset_trend > 0:
                    st.info(f"📈 **Trend**: Improving by {asset_trend:+.2f}")
                else:
                    st.warning(f"📉 **Trend**: Declining by {abs(asset_trend):.2f}")
            
            # Inventory Turnover Analysis  
            if len(ratios) > 1:
                inv_trend = ratios['Inventory_Turnover'].iloc[-1] - ratios['Inventory_Turnover'].iloc[-2]
                inv_avg = ratios['Inventory_Turnover'].mean()
                
                if inventory_turnover > inv_avg:
                    st.success(f"✅ **Inventory Turnover {inventory_turnover:.1f}x**: Above 5-year average ({inv_avg:.1f}x)")
                else:
                    st.warning(f"⚠️ **Inventory Turnover {inventory_turnover:.1f}x**: Below 5-year average ({inv_avg:.1f}x)")
                
                if inv_trend > 0:
                    st.info(f"📈 **Trend**: Improving by {inv_trend:+.1f}x")
                else:
                    st.warning(f"📉 **Trend**: Declining by {abs(inv_trend):.1f}x")
            

def create_dupont_analysis(ratios):
    """Create DuPont analysis with detailed explanations"""
    st.markdown('<h2 class="section-header">DuPont Analysis</h2>', unsafe_allow_html=True)
    
    # Explanation section
    st.markdown("""
    ### 🔍 What This Analysis Shows
    **DuPont analysis breaks down ROE into three key components to identify the drivers of shareholder returns.**
    
    - **Net Profit Margin**: Net Income ÷ Revenue (profitability efficiency)
    - **Asset Turnover**: Revenue ÷ Total Assets (asset utilization efficiency)  
    - **Equity Multiplier**: Total Assets ÷ Shareholders' Equity (financial leverage)
    - **ROE**: Net Profit Margin × Asset Turnover × Equity Multiplier
    
    **Why This Matters**: Shows whether ROE is driven by profitability, efficiency, or leverage.
    """)
    
    dupont_ratios = ['Net_Profit_Margin', 'Asset_Turnover', 'Equity_Multiplier', 'ROE_DuPont']
    available_ratios = [ratio for ratio in dupont_ratios if ratio in ratios.columns]
    
    if available_ratios:
        fig = px.line(ratios[available_ratios], 
                      title="DuPont Analysis Components - ROE Breakdown",
                      labels={'index': 'Year', 'value': 'Value'})
        
        # Add contextual description to the chart
        fig.update_layout(
            title_x=0.5,
            annotations=[
                dict(
                    x=0.5, y=1.15,
                    xref="paper", yref="paper",
                    text="📊 Each component contributes to ROE - higher values generally indicate better performance",
                    showarrow=False,
                    font=dict(size=12, color="gray")
                )
            ]
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed insights
        latest_values = ratios[available_ratios].iloc[-1]
        
        st.subheader("DuPont Analysis Assessment")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.dataframe(latest_values.to_frame('Latest Values'))
        
        with col2:
            st.markdown("### 💡 Key Insights:")
            
            profit_margin = latest_values.get('Net_Profit_Margin', 0)
            asset_turnover = latest_values.get('Asset_Turnover', 0)
            equity_multiplier = latest_values.get('Equity_Multiplier', 0)
            roe = latest_values.get('ROE_DuPont', 0)
            
            # Dynamic DuPont analysis based on actual data
            if len(ratios) > 1:
                # Profit Margin Analysis
                margin_avg = ratios['Net_Profit_Margin'].mean()
                margin_trend = ratios['Net_Profit_Margin'].iloc[-1] - ratios['Net_Profit_Margin'].iloc[-2]
                
                if profit_margin > margin_avg:
                    st.success(f"✅ **Profit Margin {profit_margin:.2%}**: Above 5-year average ({margin_avg:.2%})")
                else:
                    st.warning(f"⚠️ **Profit Margin {profit_margin:.2%}**: Below 5-year average ({margin_avg:.2%})")
                
                if margin_trend > 0:
                    st.info(f"📈 **Margin Trend**: Improving by {margin_trend:+.2%}")
                else:
                    st.warning(f"📉 **Margin Trend**: Declining by {abs(margin_trend):.2%}")
                
                # Asset Turnover Analysis
                turnover_avg = ratios['Asset_Turnover'].mean()
                turnover_trend = ratios['Asset_Turnover'].iloc[-1] - ratios['Asset_Turnover'].iloc[-2]
                
                if asset_turnover > turnover_avg:
                    st.success(f"✅ **Asset Turnover {asset_turnover:.2f}**: Above 5-year average ({turnover_avg:.2f})")
                else:
                    st.warning(f"⚠️ **Asset Turnover {asset_turnover:.2f}**: Below 5-year average ({turnover_avg:.2f})")
                
                if turnover_trend > 0:
                    st.info(f"📈 **Turnover Trend**: Improving by {turnover_trend:+.2f}")
                else:
                    st.warning(f"📉 **Turnover Trend**: Declining by {abs(turnover_trend):.2f}")
                
                # Equity Multiplier Analysis
                multiplier_avg = ratios['Equity_Multiplier'].mean()
                multiplier_trend = ratios['Equity_Multiplier'].iloc[-1] - ratios['Equity_Multiplier'].iloc[-2]
                
                if equity_multiplier > multiplier_avg:
                    st.warning(f"⚠️ **Equity Multiplier {equity_multiplier:.2f}**: Above 5-year average ({multiplier_avg:.2f}) - Higher leverage")
                else:
                    st.success(f"✅ **Equity Multiplier {equity_multiplier:.2f}**: Below 5-year average ({multiplier_avg:.2f}) - Lower leverage")
                
                if multiplier_trend > 0:
                    st.warning(f"📈 **Leverage Trend**: Increasing by {multiplier_trend:+.2f}")
                else:
                    st.info(f"📉 **Leverage Trend**: Decreasing by {abs(multiplier_trend):.2f}")
            
            # Dynamic ROE driver analysis based on actual values
            st.markdown("### 🎯 ROE Component Analysis:")
            
            # Calculate relative contributions (normalized to show which is highest)
            components = {
                'Profit Margin': profit_margin,
                'Asset Turnover': asset_turnover, 
                'Equity Multiplier': equity_multiplier
            }
            
            max_component = max(components, key=components.get)
            max_value = components[max_component]
            
            st.info(f"**Strongest Component**: {max_component} ({max_value:.3f})")
            
            # Show actual calculated ROE vs components
            calculated_roe = profit_margin * asset_turnover * equity_multiplier
            actual_roe = latest_values.get('ROE', 0)
            
            if abs(calculated_roe - actual_roe) < 0.001:
                st.success("✅ **DuPont Formula Valid**: Components correctly multiply to ROE")
            else:
                st.warning(f"⚠️ **Formula Mismatch**: Calculated ROE ({calculated_roe:.3f}) vs Actual ROE ({actual_roe:.3f})")

def create_risk_assessment(ratios):
    """Create risk assessment with detailed explanations"""
    st.markdown('<h2 class="section-header">Risk Assessment</h2>', unsafe_allow_html=True)
    
    # Explanation section
    st.markdown("""
    ### 🛡️ What This Analysis Shows
    **Risk assessment models evaluate Walmart's financial stability and quality using advanced metrics.**
    
    - **Altman Z-Score**: Bankruptcy prediction model (>2.7 = Safe, 1.8-2.7 = Grey Zone, <1.8 = Distress)
    - **Piotroski F-Score**: Financial quality assessment (0-9 scale, higher = better quality)
    
    **Why This Matters**: These models help predict financial distress and assess investment quality.
    """)
    
    # Check if risk assessment columns exist, if not create sample data for demonstration
    if 'Z_Score' not in ratios.columns or 'F_Score' not in ratios.columns:
        st.warning("⚠️ Risk assessment data not available. Creating sample data for demonstration.")
        
        # Create sample risk data for demonstration
        import numpy as np
        sample_ratios = ratios.copy()
        sample_ratios['Z_Score'] = np.random.normal(2.5, 0.5, len(ratios))
        sample_ratios['F_Score'] = np.random.randint(6, 9, len(ratios))
        
        # Create risk levels based on Z_Score
        sample_ratios['Risk_Level'] = sample_ratios['Z_Score'].apply(
            lambda x: 'Safe' if x > 2.7 else 'Grey Zone' if x > 1.8 else 'Distress'
        )
        
        # Create quality levels based on F_Score  
        sample_ratios['Quality_Level'] = sample_ratios['F_Score'].apply(
            lambda x: 'High' if x >= 8 else 'Medium' if x >= 6 else 'Low'
        )
        
        ratios = sample_ratios
    
    if 'Z_Score' in ratios.columns and 'F_Score' in ratios.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            fig_z = px.bar(ratios, x=ratios.index, y='Z_Score', color='Risk_Level',
                          title="Altman Z-Score Over Time - Bankruptcy Risk",
                          labels={'index': 'Year', 'Z_Score': 'Z-Score'})
            
            # Add contextual description to the chart
            fig_z.update_layout(
                title_x=0.5,
                annotations=[
                    dict(
                        x=0.5, y=1.15,
                        xref="paper", yref="paper",
                        text="🟢 Green = Safe (>2.7), 🟡 Yellow = Grey Zone (1.8-2.7), 🔴 Red = Distress (<1.8)",
                        showarrow=False,
                        font=dict(size=10, color="gray")
                    )
                ]
            )
            st.plotly_chart(fig_z, use_container_width=True)
        
        with col2:
            fig_f = px.bar(ratios, x=ratios.index, y='F_Score', color='Quality_Level',
                          title="Piotroski F-Score Over Time - Financial Quality",
                          labels={'index': 'Year', 'F_Score': 'F-Score'})
            
            # Add contextual description to the chart
            fig_f.update_layout(
                title_x=0.5,
                annotations=[
                    dict(
                        x=0.5, y=1.15,
                        xref="paper", yref="paper",
                        text="🟢 Green = High Quality (8-9), 🟡 Yellow = Medium (6-7), 🔴 Red = Low (0-5)",
                        showarrow=False,
                        font=dict(size=10, color="gray")
                    )
                ]
            )
            st.plotly_chart(fig_f, use_container_width=True)
        
        # Risk Assessment Summary
        latest_values = ratios.iloc[-1]
        z_score = latest_values.get('Z_Score', 0)
        f_score = latest_values.get('F_Score', 0)
        
        st.subheader("Current Risk Assessment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🚨 Altman Z-Score Analysis")
            if z_score > 3.0:
                st.success(f"✅ **Z-Score {z_score:.2f}**: Very Safe - Extremely low bankruptcy risk")
            elif z_score > 2.7:
                st.success(f"✅ **Z-Score {z_score:.2f}**: Safe - Low bankruptcy risk")
            elif z_score > 1.8:
                st.warning(f"⚠️ **Z-Score {z_score:.2f}**: Grey Zone - Monitor closely")
            else:
                st.error(f"🚨 **Z-Score {z_score:.2f}**: Distress Zone - High bankruptcy risk")
        
        with col2:
            st.markdown("### 📊 Piotroski F-Score Analysis")
            if f_score >= 8:
                st.success(f"✅ **F-Score {f_score:.0f}**: High Quality - Strong financial fundamentals")
            elif f_score >= 6:
                st.info(f"📊 **F-Score {f_score:.0f}**: Medium Quality - Decent financial health")
            else:
                st.warning(f"⚠️ **F-Score {f_score:.0f}**: Low Quality - Weak financial fundamentals")
        
        # Dynamic Overall Risk Assessment based on actual data
        st.markdown("### 🎯 Overall Risk Assessment")
        
        # Calculate risk trend
        if len(ratios) > 1:
            z_trend = ratios['Z_Score'].iloc[-1] - ratios['Z_Score'].iloc[-2]
            f_trend = ratios['F_Score'].iloc[-1] - ratios['F_Score'].iloc[-2]
            
            risk_trend = "Improving" if z_trend > 0 and f_trend >= 0 else "Declining" if z_trend < 0 or f_trend < 0 else "Stable"
            
            st.markdown(f"**Risk Trend**: {risk_trend}")
            st.markdown(f"**Z-Score Change**: {z_trend:+.2f}")
            st.markdown(f"**F-Score Change**: {f_trend:+.1f}")
        
        # Dynamic risk level based on actual thresholds
        if z_score > 2.7 and f_score >= 7:
            risk_level = "Low Risk"
            risk_color = "success"
        elif z_score > 2.0 and f_score >= 5:
            risk_level = "Moderate Risk" 
            risk_color = "info"
        else:
            risk_level = "High Risk"
            risk_color = "warning"
            
        if risk_color == "success":
            st.success(f"**Overall Assessment**: {risk_level}")
        elif risk_color == "info":
            st.info(f"**Overall Assessment**: {risk_level}")
        else:
            st.warning(f"**Overall Assessment**: {risk_level}")
    else:
        st.error("❌ Risk assessment data not available in the financial data.")

def create_peer_comparison():
    """Create comprehensive peer comparison with insights"""
    st.markdown('<h2 class="section-header">Peer Comparison Analysis (2022)</h2>', unsafe_allow_html=True)
    
    # Enhanced peer data with more metrics
    peer_data = pd.DataFrame({
        'Company': ['Walmart', 'Target', 'Costco', 'Amazon'],
        'Revenue (B)': [611, 109, 227, 575],
        'Net Income (B)': [11.7, 2.8, 5.8, 33.4],
        'ROA (%)': [4.8, 5.3, 9.1, 7.9],
        'ROE (%)': [15.2, 13.1, 25.8, 18.4],
        'Net Margin (%)': [1.9, 2.6, 2.6, 5.8],
        'Current Ratio': [0.82, 0.95, 0.99, 1.1],
        'Debt to Equity': [2.08, 1.2, 0.4, 0.3],
        'Market Cap (B)': [430, 65, 245, 1200]
    }).set_index('Company')
    
    # Display the data with formatting
    st.dataframe(peer_data.style.format({
        'Revenue (B)': '${:.0f}B',
        'Net Income (B)': '${:.1f}B', 
        'ROA (%)': '{:.1f}%',
        'ROE (%)': '{:.1f}%',
        'Net Margin (%)': '{:.1f}%',
        'Current Ratio': '{:.2f}',
        'Debt to Equity': '{:.2f}',
        'Market Cap (B)': '${:.0f}B'
    }))
    
    # Multiple visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # ROA Comparison
        fig_roa = px.bar(peer_data.reset_index(), x='Company', y='ROA (%)', 
                         title="Return on Assets - Peer Comparison",
                         color='ROA (%)',
                         color_continuous_scale='RdYlGn')
        fig_roa.update_layout(showlegend=False)
        st.plotly_chart(fig_roa, use_container_width=True)
        
        # Net Margin Comparison
        fig_margin = px.bar(peer_data.reset_index(), x='Company', y='Net Margin (%)',
                           title="Net Profit Margin - Peer Comparison", 
                           color='Net Margin (%)',
                           color_continuous_scale='RdYlGn')
        fig_margin.update_layout(showlegend=False)
        st.plotly_chart(fig_margin, use_container_width=True)
    
    with col2:
        # ROE Comparison
        fig_roe = px.bar(peer_data.reset_index(), x='Company', y='ROE (%)',
                        title="Return on Equity - Peer Comparison",
                        color='ROE (%)', 
                        color_continuous_scale='RdYlGn')
        fig_roe.update_layout(showlegend=False)
        st.plotly_chart(fig_roe, use_container_width=True)
        
        # Revenue vs Profitability Bubble Chart
        fig_bubble = px.scatter(peer_data.reset_index(), 
                               x='Revenue (B)', y='Net Margin (%)',
                               size='Net Income (B)', 
                               hover_name='Company',
                               title="Revenue vs Profitability (Bubble = Net Income)",
                               labels={'Revenue (B)': 'Revenue (Billions)', 
                                      'Net Margin (%)': 'Net Margin (%)'})
        st.plotly_chart(fig_bubble, use_container_width=True)
    
    # Competitive Analysis Insights
    st.markdown("### 🏆 Competitive Analysis")
    
    # Calculate Walmart's relative position
    walmart_data = peer_data.loc['Walmart']
    
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        st.markdown("**Walmart's Competitive Position:**")
        
        # Revenue ranking
        revenue_rank = peer_data['Revenue (B)'].rank(ascending=False)['Walmart']
        st.write(f"• **Revenue Scale**: #{int(revenue_rank)} among peers - Market leader in revenue")
        
        # ROA ranking  
        roa_rank = peer_data['ROA (%)'].rank(ascending=False)['Walmart']
        if roa_rank <= 2:
            st.write(f"• **Asset Efficiency**: #{int(roa_rank)} among peers - Strong asset utilization")
        else:
            st.write(f"• **Asset Efficiency**: #{int(roa_rank)} among peers - Room for improvement")
            
        # Margin ranking
        margin_rank = peer_data['Net Margin (%)'].rank(ascending=False)['Walmart']
        if margin_rank <= 2:
            st.write(f"• **Profitability**: #{int(margin_rank)} among peers - Competitive margins")
        else:
            st.write(f"• **Profitability**: #{int(margin_rank)} among peers - Margin pressure")
    
    with insights_col2:
        st.markdown("**Key Competitive Insights:**")
        
        # Find best performer in each category
        best_roa = peer_data['ROA (%)'].idxmax()
        best_margin = peer_data['Net Margin (%)'].idxmax()
        best_roe = peer_data['ROE (%)'].idxmax()
        
        st.write(f"• **Asset Efficiency Leader**: {best_roa} ({peer_data.loc[best_roa, 'ROA (%)']:.1f}%)")
        st.write(f"• **Margin Leader**: {best_margin} ({peer_data.loc[best_margin, 'Net Margin (%)']:.1f}%)")
        st.write(f"• **ROE Leader**: {best_roe} ({peer_data.loc[best_roe, 'ROE (%)']:.1f}%)")
        
        # Walmart vs Amazon comparison
        amazon_roa = peer_data.loc['Amazon', 'ROA (%)']
        walmart_roa = peer_data.loc['Walmart', 'ROA (%)']
        if amazon_roa > walmart_roa:
            st.write(f"• **vs Amazon**: Amazon has {amazon_roa - walmart_roa:.1f}% higher ROA")
        else:
            st.write(f"• **vs Amazon**: Walmart has {walmart_roa - amazon_roa:.1f}% higher ROA")
    
    # Strategic Recommendations
    st.markdown("### 📈 Strategic Recommendations")
    
    if peer_data.loc['Walmart', 'ROA (%)'] < peer_data['ROA (%)'].mean():
        st.warning("**Asset Efficiency**: Walmart's ROA is below peer average - focus on asset optimization")
    
    if peer_data.loc['Walmart', 'Net Margin (%)'] < peer_data['Net Margin (%)'].mean():
        st.warning("**Profitability**: Walmart's margins are below peer average - consider pricing strategy review")
    
    if peer_data.loc['Walmart', 'Current Ratio'] < 1.0:
        st.warning("**Liquidity**: Current ratio below 1.0 - monitor working capital management")
    
    st.info("**Overall**: Walmart's scale advantage in revenue is clear, but efficiency improvements could enhance profitability")

def create_ratio_trends(ratios):
    """Create ratio trends analysis with detailed explanations"""
    st.markdown('<h2 class="section-header">Ratio Trends Analysis</h2>', unsafe_allow_html=True)
    
    # Explanation section
    st.markdown("""
    ### 📈 What This Analysis Shows
    **Interactive ratio trends allow you to explore how specific financial metrics have changed over time.**
    
    **How to Use**: Select any ratio from the dropdown to see its trend and get contextual interpretation.
    
    **Why This Matters**: Trend analysis helps identify patterns, turning points, and areas needing attention.
    """)
    
    selected_ratio = st.selectbox("Select a Ratio to Visualize:", ratios.columns)
    
    if selected_ratio:
        # Get the latest and previous values for trend analysis
        latest_value = ratios[selected_ratio].iloc[-1]
        previous_value = ratios[selected_ratio].iloc[-2] if len(ratios) > 1 else latest_value
        trend_change = latest_value - previous_value
        
        # Create the chart with contextual information
        fig = px.line(ratios, x=ratios.index, y=selected_ratio, 
                      title=f"{selected_ratio} Trend Analysis",
                      labels={'index': 'Year', selected_ratio: selected_ratio})
        
        # Add trend interpretation to the chart
        trend_direction = "📈 Improving" if trend_change > 0 else "📉 Declining" if trend_change < 0 else "📊 Stable"
        fig.update_layout(
            title_x=0.5,
            annotations=[
                dict(
                    x=0.5, y=1.15,
                    xref="paper", yref="paper",
                    text=f"{trend_direction} - Latest: {latest_value:.3f} | Change: {trend_change:+.3f}",
                    showarrow=False,
                    font=dict(size=12, color="gray")
                )
            ]
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed interpretation
        st.subheader(f"📊 {selected_ratio} Interpretation")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric(
                f"Latest {selected_ratio}",
                f"{latest_value:.3f}",
                delta=f"{trend_change:+.3f}"
            )
        
        with col2:
            st.markdown("### 💡 Key Insights:")
            
            # Dynamic interpretation based on actual data analysis
            st.markdown(f"**Current Value**: {latest_value:.3f}")
            st.markdown(f"**Change from Previous**: {trend_change:+.3f}")
            
            # Calculate percentiles and performance relative to historical data
            min_val = ratios[selected_ratio].min()
            max_val = ratios[selected_ratio].max()
            mean_val = ratios[selected_ratio].mean()
            
            # Determine position relative to historical range
            if latest_value == max_val:
                st.success(f"📈 **Historical High**: This is the highest value in the dataset")
            elif latest_value == min_val:
                st.error(f"📉 **Historical Low**: This is the lowest value in the dataset")
            elif latest_value > mean_val:
                st.info(f"📊 **Above Average**: Current value ({latest_value:.3f}) is above 5-year average ({mean_val:.3f})")
            else:
                st.warning(f"📊 **Below Average**: Current value ({latest_value:.3f}) is below 5-year average ({mean_val:.3f})")
            
            # Trend strength analysis
            if len(ratios) > 2:
                recent_trend = ratios[selected_ratio].iloc[-3:].pct_change().mean()
                if recent_trend > 0.05:
                    st.success(f"🚀 **Strong Upward Trend**: Growing by {recent_trend:.1%} recently")
                elif recent_trend > 0:
                    st.info(f"📈 **Moderate Growth**: Growing by {recent_trend:.1%} recently")
                elif recent_trend > -0.05:
                    st.warning(f"📉 **Moderate Decline**: Declining by {abs(recent_trend):.1%} recently")
                else:
                    st.error(f"📉 **Strong Decline**: Declining by {abs(recent_trend):.1%} recently")
            
            # Volatility analysis
            if len(ratios) > 2:
                volatility = ratios[selected_ratio].std()
                st.markdown(f"**Volatility**: {volatility:.3f} (standard deviation)")
                
                if volatility > ratios[selected_ratio].mean() * 0.2:
                    st.warning("⚠️ **High Volatility**: This metric shows significant variation over time")
                else:
                    st.info("📊 **Low Volatility**: This metric has been relatively stable")

def main():
    """Main dashboard function"""
    st.markdown('<h1 class="main-header">Walmart Financial Analysis Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    financial_data, ratios = load_data()
    
    if financial_data is None or ratios is None:
        st.error("Failed to load financial data. Please check your data files.")
        return
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    analysis_type = st.sidebar.radio(
        "Choose Analysis Type:",
        ["Overview", "Dynamic Insights", "Liquidity Analysis", "Profitability Analysis", "Leverage Analysis", 
         "Efficiency Analysis", "DuPont Analysis", "Risk Assessment", "Peer Comparison", "Ratio Trends"]
    )
    
    # Overview Section
    if analysis_type == "Overview":
        st.header("Company Overview")
        st.write("This dashboard provides a comprehensive financial analysis of Walmart Inc. (WMT).")
        
        st.subheader("Latest Financial Snapshot")
        create_metrics_row(ratios, financial_data)
        
        st.subheader("All Financial Ratios")
        # Filter out non-numeric columns for display
        numeric_ratios = ratios.select_dtypes(include=[np.number])
        st.dataframe(numeric_ratios.T)
        
        st.subheader("Financial Insights & Analysis")
        
        # Calculate insights from the data
        latest_year = ratios.index.max()
        latest_ratios = ratios.loc[latest_year]
        
        # Revenue and Growth Analysis
        revenue_data = financial_data['income_statement']['Revenue']
        revenue_growth = ((revenue_data.iloc[0] - revenue_data.iloc[-1]) / revenue_data.iloc[-1]) * 100
        
        # Profitability Analysis
        net_income_data = financial_data['income_statement']['Net Income']
        profit_growth = ((net_income_data.iloc[0] - net_income_data.iloc[-1]) / net_income_data.iloc[-1]) * 100
        
        # Liquidity Analysis
        current_ratio = latest_ratios.get('Current_Ratio', 0)
        liquidity_status = "Strong" if current_ratio > 1.0 else "Concerning"
        
        # Risk Assessment
        z_score = latest_ratios.get('Z_Score', 0)
        risk_level = latest_ratios.get('Risk_Level', 'Unknown')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Growth & Performance")
            if revenue_growth > 0:
                st.success(f"**Revenue Growth**: {revenue_growth:.1f}% over 5 years - Strong top-line growth")
            else:
                st.error(f"**Revenue Growth**: {revenue_growth:.1f}% over 5 years - Declining revenue")
            
            if profit_growth > 0:
                st.success(f"**Profit Growth**: {profit_growth:.1f}% over 5 years - Improving profitability")
            else:
                st.warning(f"**Profit Growth**: {profit_growth:.1f}% over 5 years - Profit pressure")
            
            roe = latest_ratios.get('ROE', 0)
            if roe > 0.15:
                st.success(f"**ROE**: {roe:.1%} - Excellent shareholder returns")
            elif roe > 0.10:
                st.info(f"**ROE**: {roe:.1%} - Good shareholder returns")
            else:
                st.warning(f"**ROE**: {roe:.1%} - Below average returns")
        
        with col2:
            st.markdown("### 💰 Financial Health")
            if liquidity_status == "Strong":
                st.success(f"**Liquidity**: Current ratio {current_ratio:.2f} - Strong short-term liquidity")
            else:
                st.warning(f"**Liquidity**: Current ratio {current_ratio:.2f} - Below 1.0, potential liquidity concerns")
            
            if z_score > 3.0:
                st.success(f"**Financial Stability**: Z-Score {z_score:.2f} - Very stable financial position")
            elif z_score > 2.7:
                st.info(f"**Financial Stability**: Z-Score {z_score:.2f} - Safe financial position")
            else:
                st.warning(f"**Financial Stability**: Z-Score {z_score:.2f} - Monitor closely")
            
            debt_to_equity = latest_ratios.get('Debt_to_Equity', 0)
            if debt_to_equity < 0.5:
                st.success(f"**Leverage**: {debt_to_equity:.2f} - Conservative debt levels")
            elif debt_to_equity < 1.0:
                st.info(f"**Leverage**: {debt_to_equity:.2f} - Moderate debt levels")
            else:
                st.warning(f"**Leverage**: {debt_to_equity:.2f} - High debt levels")
        
        # Strategic Insights
        st.markdown("### 🎯 Strategic Insights")
        insights_col1, insights_col2 = st.columns(2)
        
        with insights_col1:
            st.markdown("**Strengths:**")
            if revenue_growth > 0:
                st.write("• Consistent revenue growth demonstrates market leadership")
            if roe > 0.10:
                st.write("• Strong return on equity shows efficient capital utilization")
            if z_score > 2.7:
                st.write("• Solid financial stability reduces bankruptcy risk")
            
        with insights_col2:
            st.markdown("**Areas of Concern:**")
            if current_ratio < 1.0:
                st.write("• Low current ratio may indicate liquidity pressure")
            if profit_growth < 0:
                st.write("• Declining profitability needs attention")
            if debt_to_equity > 1.0:
                st.write("• High leverage increases financial risk")
        
        # Investment Recommendation
        st.markdown("### 📊 Investment Outlook")
        if roe > 0.12 and z_score > 2.7 and revenue_growth > 0:
            st.success("**Overall Assessment**: Strong financial position with good growth prospects")
        elif roe > 0.08 and z_score > 2.0:
            st.info("**Overall Assessment**: Stable company with moderate growth potential")
        else:
            st.warning("**Overall Assessment**: Mixed signals - requires careful monitoring")

def create_dynamic_insights(ratios, financial_data):
    """Create comprehensive dynamic insights that update in real-time"""
    st.markdown('<h2 class="section-header">🔍 Dynamic Financial Insights</h2>', unsafe_allow_html=True)
    
    latest_year = ratios.index.max()
    latest_ratios = ratios.loc[latest_year]
    
    # Calculate trends and patterns
    trends = calculate_trends(ratios, financial_data)
    alerts = generate_financial_alerts(ratios, financial_data)
    forecasts = generate_forecasts(ratios, financial_data)
    
    # Real-time Performance Dashboard
    st.markdown("### 📈 Real-Time Performance Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📊 Trend Analysis**")
        for trend in trends[:3]:  # Show top 3 trends
            if trend['direction'] == 'improving':
                st.success(f"✅ {trend['metric']}: {trend['change']:.1f}% improvement")
            elif trend['direction'] == 'declining':
                st.error(f"❌ {trend['metric']}: {trend['change']:.1f}% decline")
            else:
                st.info(f"📊 {trend['metric']}: {trend['change']:.1f}% change")
    
    with col2:
        st.markdown("**⚠️ Financial Alerts**")
        if alerts:
            for alert in alerts[:3]:  # Show top 3 alerts
                if alert['severity'] == 'high':
                    st.error(f"🚨 {alert['message']}")
                elif alert['severity'] == 'medium':
                    st.warning(f"⚠️ {alert['message']}")
                else:
                    st.info(f"ℹ️ {alert['message']}")
        else:
            st.success("✅ No critical alerts")
    
    with col3:
        st.markdown("**🔮 Forecast Indicators**")
        for forecast in forecasts[:3]:  # Show top 3 forecasts
            if forecast['direction'] == 'positive':
                st.success(f"📈 {forecast['metric']}: {forecast['outlook']}")
            elif forecast['direction'] == 'negative':
                st.error(f"📉 {forecast['metric']}: {forecast['outlook']}")
            else:
                st.info(f"📊 {forecast['metric']}: {forecast['outlook']}")
    
    # Advanced Analytics
    st.markdown("### 🧠 Advanced Analytics")
    
    analytics_col1, analytics_col2 = st.columns(2)
    
    with analytics_col1:
        st.markdown("**📊 Efficiency Metrics**")
        asset_turnover = latest_ratios.get('Asset_Turnover', 0)
        inventory_turnover = latest_ratios.get('Inventory_Turnover', 0)
        
        efficiency_score = calculate_efficiency_score(ratios)
        st.metric("Efficiency Score", f"{efficiency_score:.1f}/10", 
                 delta=f"{efficiency_score - 7:.1f}" if efficiency_score > 7 else None)
        
        if asset_turnover > 2.0:
            st.success(f"✅ Asset Turnover: {asset_turnover:.2f} - Excellent asset utilization")
        elif asset_turnover > 1.5:
            st.info(f"📊 Asset Turnover: {asset_turnover:.2f} - Good asset utilization")
        else:
            st.warning(f"⚠️ Asset Turnover: {asset_turnover:.2f} - Needs improvement")
    
    with analytics_col2:
        st.markdown("**💰 Cash Flow Health**")
        operating_cf = latest_ratios.get('Operating_CF_Margin', 0)
        free_cf = latest_ratios.get('Free_CF_Margin', 0)
        
        cash_flow_score = (operating_cf + free_cf) * 50  # Convert to 0-10 scale
        st.metric("Cash Flow Score", f"{cash_flow_score:.1f}/10", 
                 delta=f"{cash_flow_score - 5:.1f}" if cash_flow_score > 5 else None)
        
        if operating_cf > 0.05:
            st.success(f"✅ Operating CF Margin: {operating_cf:.2%} - Strong cash generation")
        else:
            st.warning(f"⚠️ Operating CF Margin: {operating_cf:.2%} - Monitor cash flow")
    
    # Risk Monitoring
    st.markdown("### 🛡️ Real-Time Risk Monitoring")
    
    risk_col1, risk_col2, risk_col3 = st.columns(3)
    
    with risk_col1:
        st.markdown("**🔒 Liquidity Risk**")
        current_ratio = latest_ratios.get('Current_Ratio', 0)
        quick_ratio = latest_ratios.get('Quick_Ratio', 0)
        
        if current_ratio > 1.0:
            st.success(f"✅ Low Risk - Current Ratio: {current_ratio:.2f}")
        else:
            st.error(f"🚨 High Risk - Current Ratio: {current_ratio:.2f}")
    
    with risk_col2:
        st.markdown("**⚖️ Leverage Risk**")
        debt_to_equity = latest_ratios.get('Debt_to_Equity', 0)
        
        if debt_to_equity < 0.5:
            st.success(f"✅ Low Risk - D/E: {debt_to_equity:.2f}")
        elif debt_to_equity < 1.0:
            st.warning(f"⚠️ Medium Risk - D/E: {debt_to_equity:.2f}")
        else:
            st.error(f"🚨 High Risk - D/E: {debt_to_equity:.2f}")
    
    with risk_col3:
        st.markdown("**📊 Financial Stability**")
        z_score = latest_ratios.get('Z_Score', 0)
        
        if z_score > 3.0:
            st.success(f"✅ Very Safe - Z-Score: {z_score:.2f}")
        elif z_score > 2.7:
            st.info(f"📊 Safe - Z-Score: {z_score:.2f}")
        else:
            st.warning(f"⚠️ Monitor - Z-Score: {z_score:.2f}")
    
    # Performance Benchmarking
    st.markdown("### 🏆 Performance Benchmarking")
    
    benchmark_col1, benchmark_col2 = st.columns(2)
    
    with benchmark_col1:
        st.markdown("**📈 Growth Benchmarks**")
        revenue_data = financial_data['income_statement']['Revenue']
        revenue_growth_5y = ((revenue_data.iloc[0] - revenue_data.iloc[-1]) / revenue_data.iloc[-1]) * 100
        
        if revenue_growth_5y > 15:
            st.success(f"🚀 Exceptional Growth: {revenue_growth_5y:.1f}% (5-year)")
        elif revenue_growth_5y > 8:
            st.info(f"📈 Strong Growth: {revenue_growth_5y:.1f}% (5-year)")
        else:
            st.warning(f"📊 Moderate Growth: {revenue_growth_5y:.1f}% (5-year)")
    
    with benchmark_col2:
        st.markdown("**💎 Profitability Benchmarks**")
        net_margin = latest_ratios.get('Net_Profit_Margin', 0)
        
        if net_margin > 0.05:
            st.success(f"💰 Excellent Margins: {net_margin:.2%}")
        elif net_margin > 0.03:
            st.info(f"📊 Good Margins: {net_margin:.2%}")
        else:
            st.warning(f"⚠️ Thin Margins: {net_margin:.2%}")
    

def calculate_trends(ratios, financial_data):
    """Calculate trend analysis for all key metrics"""
    trends = []
    
    # Revenue trend
    revenue_data = financial_data['income_statement']['Revenue']
    revenue_trend = ((revenue_data.iloc[0] - revenue_data.iloc[-1]) / revenue_data.iloc[-1]) * 100
    trends.append({
        'metric': 'Revenue Growth',
        'change': revenue_trend,
        'direction': 'improving' if revenue_trend > 0 else 'declining'
    })
    
    # Profit trend
    profit_data = financial_data['income_statement']['Net Income']
    profit_trend = ((profit_data.iloc[0] - profit_data.iloc[-1]) / profit_data.iloc[-1]) * 100
    trends.append({
        'metric': 'Net Income Growth',
        'change': profit_trend,
        'direction': 'improving' if profit_trend > 0 else 'declining'
    })
    
    # ROE trend
    roe_trend = ratios['ROE'].iloc[0] - ratios['ROE'].iloc[-1]
    trends.append({
        'metric': 'ROE Change',
        'change': roe_trend * 100,
        'direction': 'improving' if roe_trend > 0 else 'declining'
    })
    
    # Current ratio trend
    cr_trend = ratios['Current_Ratio'].iloc[0] - ratios['Current_Ratio'].iloc[-1]
    trends.append({
        'metric': 'Liquidity Change',
        'change': cr_trend * 100,
        'direction': 'improving' if cr_trend > 0 else 'declining'
    })
    
    return sorted(trends, key=lambda x: abs(x['change']), reverse=True)

def generate_financial_alerts(ratios, financial_data):
    """Generate real-time financial alerts"""
    alerts = []
    latest_ratios = ratios.iloc[0]
    
    # Liquidity alert
    if latest_ratios.get('Current_Ratio', 0) < 1.0:
        alerts.append({
            'severity': 'high',
            'message': 'Current ratio below 1.0 - liquidity concern'
        })
    
    # Leverage alert
    if latest_ratios.get('Debt_to_Equity', 0) > 1.5:
        alerts.append({
            'severity': 'medium',
            'message': 'High debt-to-equity ratio detected'
        })
    
    # Profitability alert
    if latest_ratios.get('Net_Profit_Margin', 0) < 0.02:
        alerts.append({
            'severity': 'medium',
            'message': 'Low profit margins - efficiency review needed'
        })
    
    # Z-score alert
    if latest_ratios.get('Z_Score', 0) < 2.7:
        alerts.append({
            'severity': 'high',
            'message': 'Financial stability risk - Z-score below safe threshold'
        })
    
    return alerts

def generate_forecasts(ratios, financial_data):
    """Generate simple forecasts based on trends"""
    forecasts = []
    
    # Revenue forecast
    revenue_data = financial_data['income_statement']['Revenue']
    revenue_growth = ((revenue_data.iloc[0] - revenue_data.iloc[1]) / revenue_data.iloc[1])
    forecasts.append({
        'metric': 'Revenue Forecast',
        'direction': 'positive' if revenue_growth > 0 else 'negative',
        'outlook': f"Projected {revenue_growth*100:+.1f}% growth trend"
    })
    
    # ROE forecast
    roe_trend = ratios['ROE'].iloc[0] - ratios['ROE'].iloc[1]
    forecasts.append({
        'metric': 'ROE Forecast',
        'direction': 'positive' if roe_trend > 0 else 'negative',
        'outlook': f"ROE trend {roe_trend*100:+.1f}%"
    })
    
    return forecasts

def calculate_efficiency_score(ratios):
    """Calculate overall efficiency score (0-10)"""
    latest = ratios.iloc[0]
    
    # Asset turnover score (0-3)
    asset_score = min(latest.get('Asset_Turnover', 0) / 2.0 * 3, 3)
    
    # Inventory turnover score (0-3)
    inv_score = min(latest.get('Inventory_Turnover', 0) / 10.0 * 3, 3)
    
    # ROE score (0-4)
    roe_score = min(latest.get('ROE', 0) / 0.15 * 4, 4)
    
    return asset_score + inv_score + roe_score

def main():
    """Main dashboard function"""
    st.markdown('<h1 class="main-header">Walmart Financial Analysis Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    financial_data, ratios = load_data()
    
    if financial_data is None or ratios is None:
        st.error("Failed to load financial data. Please check your data files.")
        return
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    analysis_type = st.sidebar.radio(
        "Choose Analysis Type:",
        ["Overview", "Dynamic Insights", "Liquidity Analysis", "Profitability Analysis", "Leverage Analysis", 
         "Efficiency Analysis", "DuPont Analysis", "Risk Assessment", "Peer Comparison", "Ratio Trends"]
    )
    
    # Overview Section
    if analysis_type == "Overview":
        st.header("Company Overview")
        st.write("This dashboard provides a comprehensive financial analysis of Walmart Inc. (WMT).")
        
        st.subheader("Latest Financial Snapshot")
        create_metrics_row(ratios, financial_data)
        
        st.subheader("All Financial Ratios")
        # Filter out non-numeric columns for display
        numeric_ratios = ratios.select_dtypes(include=[np.number])
        st.dataframe(numeric_ratios.T)
        
        st.subheader("Financial Insights & Analysis")
        
        # Calculate insights from the data
        latest_year = ratios.index.max()
        latest_ratios = ratios.loc[latest_year]
        
        # Revenue and Growth Analysis
        revenue_data = financial_data['income_statement']['Revenue']
        revenue_growth = ((revenue_data.iloc[0] - revenue_data.iloc[-1]) / revenue_data.iloc[-1]) * 100
        
        # Profitability Analysis
        net_income_data = financial_data['income_statement']['Net Income']
        profit_growth = ((net_income_data.iloc[0] - net_income_data.iloc[-1]) / net_income_data.iloc[-1]) * 100
        
        # Liquidity Analysis
        current_ratio = latest_ratios.get('Current_Ratio', 0)
        liquidity_status = "Strong" if current_ratio > 1.0 else "Concerning"
        
        # Risk Assessment
        z_score = latest_ratios.get('Z_Score', 0)
        risk_level = latest_ratios.get('Risk_Level', 'Unknown')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Growth & Performance")
            if revenue_growth > 0:
                st.success(f"**Revenue Growth**: {revenue_growth:.1f}% over 5 years - Strong top-line growth")
            else:
                st.error(f"**Revenue Growth**: {revenue_growth:.1f}% over 5 years - Declining revenue")
            
            if profit_growth > 0:
                st.success(f"**Profit Growth**: {profit_growth:.1f}% over 5 years - Improving profitability")
            else:
                st.warning(f"**Profit Growth**: {profit_growth:.1f}% over 5 years - Profit pressure")
            
            roe = latest_ratios.get('ROE', 0)
            if roe > 0.15:
                st.success(f"**ROE**: {roe:.1%} - Excellent shareholder returns")
            elif roe > 0.10:
                st.info(f"**ROE**: {roe:.1%} - Good shareholder returns")
            else:
                st.warning(f"**ROE**: {roe:.1%} - Below average returns")
        
        with col2:
            st.markdown("### 💰 Financial Health")
            if liquidity_status == "Strong":
                st.success(f"**Liquidity**: Current ratio {current_ratio:.2f} - Strong short-term liquidity")
            else:
                st.warning(f"**Liquidity**: Current ratio {current_ratio:.2f} - Below 1.0, potential liquidity concerns")
            
            if z_score > 3.0:
                st.success(f"**Financial Stability**: Z-Score {z_score:.2f} - Very stable financial position")
            elif z_score > 2.7:
                st.info(f"**Financial Stability**: Z-Score {z_score:.2f} - Safe financial position")
            else:
                st.warning(f"**Financial Stability**: Z-Score {z_score:.2f} - Monitor closely")
            
            debt_to_equity = latest_ratios.get('Debt_to_Equity', 0)
            if debt_to_equity < 0.5:
                st.success(f"**Leverage**: {debt_to_equity:.2f} - Conservative debt levels")
            elif debt_to_equity < 1.0:
                st.info(f"**Leverage**: {debt_to_equity:.2f} - Moderate debt levels")
            else:
                st.warning(f"**Leverage**: {debt_to_equity:.2f} - High debt levels")
        
        # Strategic Insights
        st.markdown("### 🎯 Strategic Insights")
        insights_col1, insights_col2 = st.columns(2)
        
        with insights_col1:
            st.markdown("**Strengths:**")
            if revenue_growth > 0:
                st.write("• Consistent revenue growth demonstrates market leadership")
            if roe > 0.10:
                st.write("• Strong return on equity shows efficient capital utilization")
            if z_score > 2.7:
                st.write("• Solid financial stability reduces bankruptcy risk")
            
        with insights_col2:
            st.markdown("**Areas of Concern:**")
            if current_ratio < 1.0:
                st.write("• Low current ratio may indicate liquidity pressure")
            if profit_growth < 0:
                st.write("• Declining profitability needs attention")
            if debt_to_equity > 1.0:
                st.write("• High leverage increases financial risk")
        
        # Investment Recommendation
        st.markdown("### 📊 Investment Outlook")
        if roe > 0.12 and z_score > 2.7 and revenue_growth > 0:
            st.success("**Overall Assessment**: Strong financial position with good growth prospects")
        elif roe > 0.08 and z_score > 2.0:
            st.info("**Overall Assessment**: Stable company with moderate growth potential")
        else:
            st.warning("**Overall Assessment**: Mixed signals - requires careful monitoring")
    
    # Dynamic Insights Section
    elif analysis_type == "Dynamic Insights":
        create_dynamic_insights(ratios, financial_data)
    
    # Individual analysis sections
    elif analysis_type == "Liquidity Analysis":
        create_liquidity_analysis(ratios)
    elif analysis_type == "Profitability Analysis":
        create_profitability_analysis(ratios)
    elif analysis_type == "Leverage Analysis":
        create_leverage_analysis(ratios)
    elif analysis_type == "Efficiency Analysis":
        create_efficiency_analysis(ratios)
    elif analysis_type == "DuPont Analysis":
        create_dupont_analysis(ratios)
    elif analysis_type == "Risk Assessment":
        create_risk_assessment(ratios)
    elif analysis_type == "Peer Comparison":
        create_peer_comparison()
    elif analysis_type == "Ratio Trends":
        create_ratio_trends(ratios)
    

if __name__ == "__main__":
    main()