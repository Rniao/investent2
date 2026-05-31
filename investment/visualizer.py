import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from typing import List, Dict

class InvestmentVisualizer:
    def __init__(self):
        plt.rcParams['axes.unicode_minus'] = False

    def plot_npv_curve(self, results: List[Dict]):
        years = [r['投资年份'] for r in results]
        npvs = [r['NPV'] if r['NPV'] != -float('inf') else 0 for r in results]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(years, npvs, marker='o', linewidth=2, markersize=8, color='#2E86AB')
        ax.fill_between(years, npvs, alpha=0.3, color='#2E86AB')
        
        max_idx = np.argmax(npvs)
        ax.scatter([years[max_idx]], [npvs[max_idx]], color='red', s=200, zorder=5, 
                  label=f'Best Timing (Year {years[max_idx]})', marker='*')

        ax.set_xlabel('Wait Years', fontsize=12)
        ax.set_ylabel('NPV (10K)', fontsize=12)
        ax.set_title('NPV vs Wait Time', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10)
        
        st.pyplot(fig)
        plt.close()

    def plot_investment_timing(self, results: List[Dict]):
        valid_results = [r for r in results if r['NPV'] != -float('inf')]
        
        years = [r['投资年份'] for r in valid_results]
        npvs = [r['NPV'] for r in valid_results]
        returns = [r['累计收益'] for r in valid_results]
        costs = [r['累计成本'] for r in valid_results]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        bars1 = ax1.bar(years, returns, alpha=0.7, color='#4CAF50', label='Total Returns')
        bars2 = ax1.bar(years, costs, alpha=0.7, color='#F44366', label='Total Costs')
        ax1.set_xlabel('Investment Year', fontsize=12)
        ax1.set_ylabel('Amount (10K)', fontsize=12)
        ax1.set_title('Returns vs Costs', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3, axis='y')

        colors = ['#FF6B6B' if npv < 0 else '#4ECDC4' for npv in npvs]
        ax2.bar(years, npvs, color=colors, alpha=0.7)
        ax2.axhline(y=0, color='black', linestyle='--', linewidth=1)
        ax2.set_xlabel('Investment Year', fontsize=12)
        ax2.set_ylabel('NPV (10K)', fontsize=12)
        ax2.set_title('NPV by Investment Year', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    def plot_sensitivity_analysis(self, sensitivity_df: pd.DataFrame):
        fig, ax = plt.subplots(figsize=(10, 6))

        colors = plt.cm.viridis(np.linspace(0, 1, len(sensitivity_df)))
        bars = ax.bar(sensitivity_df['折现率'], sensitivity_df['最佳投资年份'], 
                     color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)

        for bar, npv in zip(bars, sensitivity_df['最大NPV']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'NPV={npv:.1f}',
                   ha='center', va='bottom', fontsize=9)

        ax.set_xlabel('Discount Rate', fontsize=12)
        ax.set_ylabel('Best Invest Year', fontsize=12)
        ax.set_title('Discount Rate Sensitivity', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        st.pyplot(fig)
        plt.close()

    def plot_cash_flow_diagram(self, investment_year: int, cash_flows: List[float], 
                              discount_rate: float):
        years = list(range(investment_year + 1, investment_year + len(cash_flows) + 1))
        
        fig, ax = plt.subplots(figsize=(12, 5))
        
        for i, (year, flow) in enumerate(zip(years, cash_flows)):
            color = 'green' if flow > 0 else 'red'
            ax.arrow(year, 0, 0, flow, head_width=0.3, head_length=abs(flow)*0.1, 
                    fc=color, ec=color, linewidth=2)
            ax.text(year, flow/2, f'{flow:.1f}', ha='center', va='center', 
                   fontsize=9, fontweight='bold')

        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Cash Flow (10K)', fontsize=12)
        ax.set_title(f'Cash Flow (Invest at Year {investment_year})', fontsize=14, fontweight='bold')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax.grid(True, alpha=0.3)

        st.pyplot(fig)
        plt.close()