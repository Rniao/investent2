from typing import Dict, List

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st


class InvestmentVisualizer:
    def __init__(self):
        self._configure_chinese_font()

    @staticmethod
    def _configure_chinese_font():
        candidate_fonts = [
            'Microsoft YaHei',
            'SimHei',
            'Noto Sans CJK SC',
            'Source Han Sans SC',
            'Arial Unicode MS'
        ]
        installed_fonts = {font.name for font in fm.fontManager.ttflist}
        selected_fonts = [font for font in candidate_fonts if font in installed_fonts]
        if selected_fonts:
            plt.rcParams['font.sans-serif'] = selected_fonts + ['DejaVu Sans']
        else:
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

    @staticmethod
    def _valid_results(results: List[Dict]) -> List[Dict]:
        return [result for result in results if result.get('是否有效')]

    def plot_npv_curve(self, results: List[Dict]):
        valid_results = self._valid_results(results)
        if not valid_results:
            st.warning("没有有效投资年份，无法绘制 NPV 曲线。")
            return

        years = [result['投资年份'] for result in valid_results]
        npvs = [result['NPV'] for result in valid_results]
        best_idx = int(np.argmax(npvs))

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(years, npvs, marker='o', linewidth=2.4, markersize=7, color='#1F77B4')
        ax.fill_between(years, npvs, alpha=0.18, color='#1F77B4')
        ax.scatter(
            [years[best_idx]],
            [npvs[best_idx]],
            color='#D62728',
            s=180,
            zorder=5,
            label=f"Best timing: Year {years[best_idx]}"
        )

        ax.axhline(y=0, color='#333333', linestyle='--', linewidth=1)
        ax.set_xlabel('等待年限（年）', fontsize=12)
        ax.set_ylabel('NPV（万元）', fontsize=12)
        ax.set_title('NPV 随等待时间变化', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.25)
        ax.legend(fontsize=10)

        st.pyplot(fig)
        plt.close(fig)

    def plot_investment_timing(self, results: List[Dict]):
        valid_results = self._valid_results(results)
        if not valid_results:
            st.warning("没有有效投资年份，无法绘制投资时点分析图。")
            return

        years = [result['投资年份'] for result in valid_results]
        returns = [result['累计收益'] for result in valid_results]
        costs = [result['投资成本'] for result in valid_results]
        npvs = [result['NPV'] for result in valid_results]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        width = 0.36
        x = np.arange(len(years))
        ax1.bar(x - width / 2, returns, width, color='#2CA02C', alpha=0.78, label='累计收益')
        ax1.bar(x + width / 2, costs, width, color='#FF7F0E', alpha=0.78, label='投资成本')
        ax1.set_xticks(x)
        ax1.set_xticklabels(years)
        ax1.set_xlabel('Waiting Years', fontsize=12)
        ax1.set_ylabel('Amount (10k CNY)', fontsize=12)
        ax1.set_title('Returns vs Investment Cost', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.25, axis='y')

        colors = ['#C44E52' if npv < 0 else '#4C72B0' for npv in npvs]
        ax2.bar(years, npvs, color=colors, alpha=0.82)
        ax2.axhline(y=0, color='#333333', linestyle='--', linewidth=1)
        ax2.set_xlabel('等待年限（年）', fontsize=12)
        ax2.set_ylabel('NPV（万元）', fontsize=12)
        ax2.set_title('各投资年份 NPV', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.25, axis='y')

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    def plot_sensitivity_analysis(self, sensitivity_df: pd.DataFrame):
        if sensitivity_df.empty:
            st.warning("No data available for sensitivity analysis display.")
            return

        fig, ax = plt.subplots(figsize=(10, 5))

        x = np.arange(len(sensitivity_df))
        years = sensitivity_df['最佳投资年份'].astype(float).to_numpy()
        colors = ['#C44E52' if status == 'reject' else '#4C72B0'
                  for status in sensitivity_df['推荐状态']]

        ax.plot(x, years, color='#4C72B0', linewidth=2, alpha=0.65, zorder=2)
        ax.scatter(
            x,
            years,
            s=120,
            color=colors,
            edgecolor='#222222',
            linewidth=0.8,
            zorder=3
        )

        for idx, (year, npv) in enumerate(zip(years, sensitivity_df['最大NPV'])):
            ax.text(
                idx,
                year + 0.12,
                f"NPV={npv:.1f}",
                ha='center',
                va='bottom',
                fontsize=9
            )

        ax.set_xticks(x)
        ax.set_xticklabels(sensitivity_df['折现率'])
        max_year = max(years) if len(years) else 0
        ax.set_ylim(-0.45, max(1.0, max_year + 0.8))
        ax.set_yticks(range(0, int(max(1, max_year)) + 1))
        ax.set_xlabel('折现率', fontsize=12)
        ax.set_ylabel('推荐等待年限（年）', fontsize=12)
        ax.set_title('折现率敏感性分析', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.25, axis='y')

        st.pyplot(fig)
        plt.close(fig)

    def plot_cash_flow_diagram(self, investment_year: int, cash_flows: List[float]):
        if not cash_flows:
            st.warning("No cash flow data available for current plan.")
            return

        years = list(range(investment_year + 1, investment_year + len(cash_flows) + 1))
        fig, ax = plt.subplots(figsize=(12, 5))

        ax.bar(years, cash_flows, color='#2CA02C', alpha=0.76)
        ax.axhline(y=0, color='#333333', linewidth=1)
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Net Cash Flow (10k CNY)', fontsize=12)
        ax.set_title(f'Net Cash Flow After Year {investment_year} Investment', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.25, axis='y')

        st.pyplot(fig)
        plt.close(fig)
