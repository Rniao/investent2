import pandas as pd
import streamlit as st

from calculator import InvestmentCalculator
from validator import InvestmentValidator
from visualizer import InvestmentVisualizer


def format_percent(value):
    if value is None:
        return '无法计算'
    return f'{value * 100:.2f}%'


def format_years(value):
    if value is None:
        return '未回收'
    return f'{value:.2f} 年'


def format_money(value):
    if value is None:
        return '不适用'
    return f'{value:.2f}'


st.set_page_config(page_title="投资时机决策模拟器", layout="wide")

st.title("投资时机决策模拟器")
st.caption("基于净现值、内部收益率和回收期的确定型投资时机决策支持工具")

st.sidebar.header("输入参数")

with st.sidebar.expander("基础参数", expanded=True):
    current_investment_cost = st.number_input("当前投资成本（万元）", min_value=0.0, value=1000.0, step=10.0)
    current_annual_return = st.number_input("当前年收益（万元）", min_value=0.0, value=200.0, step=10.0)
    future_growth_rate = st.number_input("未来收益增长率（%/年）", min_value=0.0, max_value=100.0, value=5.0, step=0.5)
    discount_rate = st.number_input("折现率（%/年）", min_value=0.0, max_value=50.0, value=8.0, step=0.5)
    project_lifetime = st.number_input("项目寿命（年）", min_value=1, max_value=50, value=10, step=1)

with st.sidebar.expander("等待参数", expanded=True):
    max_wait_years = st.number_input("最大等待年限（年）", min_value=0, max_value=20, value=5, step=1)
    cost_increase_rate = st.number_input("等待导致的成本上升率（%/年）", min_value=0.0, max_value=50.0, value=3.0, step=0.5)
    opportunity_loss_rate = st.number_input("机会损失率（%/年）", min_value=0.0, max_value=50.0, value=2.0, step=0.5)

with st.sidebar.expander("现实拓展选项", expanded=False):
    growth_decline_enabled = st.checkbox("收益增长率逐年下降", value=False)
    cost_increase_yearly_enabled = st.checkbox("投资成本额外逐年上升", value=False)
    market_window_enabled = st.checkbox("等待太久会失去市场窗口", value=False)
    early_investment_bonus_enabled = st.checkbox("立即投资可获得市场占有率收益", value=False)

    growth_decline_amount = 0.0
    if growth_decline_enabled:
        growth_decline_amount = st.number_input("增长率年下降量（%/年）", min_value=0.0, max_value=10.0, value=0.5, step=0.1)

    cost_increase_yearly_rate = 0.0
    if cost_increase_yearly_enabled:
        cost_increase_yearly_rate = st.number_input("额外成本年上升率（%/年）", min_value=0.0, max_value=20.0, value=2.0, step=0.5)

    market_window_years = 20
    if market_window_enabled:
        market_window_years = st.number_input("市场窗口期（年）", min_value=0, max_value=20, value=8, step=1)

    early_bonus_rate = 0.0
    if early_investment_bonus_enabled:
        early_bonus_rate = st.number_input("立即投资收益率加成（%/年）", min_value=0.0, max_value=20.0, value=1.0, step=0.5)

calculator = InvestmentCalculator(
    current_investment_cost=current_investment_cost,
    current_annual_return=current_annual_return,
    future_growth_rate=future_growth_rate / 100,
    discount_rate=discount_rate / 100,
    project_lifetime=project_lifetime,
    max_wait_years=max_wait_years,
    cost_increase_rate=cost_increase_rate / 100,
    opportunity_loss_rate=opportunity_loss_rate / 100,
    growth_decline_rate=growth_decline_amount / 100,
    cost_increase_yearly_rate=cost_increase_yearly_rate / 100,
    market_window_years=market_window_years,
    early_bonus_rate=early_bonus_rate / 100
)

results = calculator.calculate_all_scenarios()
recommendation = calculator.get_recommendation()
best_scenario = recommendation['best_scenario']
current_scenario = recommendation['current_scenario']
visualizer = InvestmentVisualizer()

st.subheader("决策建议")
if recommendation['status'] == 'reject':
    st.error(recommendation['message'])
elif recommendation['status'] == 'invalid':
    st.warning(recommendation['message'])
else:
    st.success(recommendation['message'])

metric_cols = st.columns(4)
with metric_cols[0]:
    st.metric("推荐方案", recommendation['decision'])
with metric_cols[1]:
    st.metric("最高 NPV（万元）", '不适用' if best_scenario is None else f"{best_scenario['NPV']:.2f}")
with metric_cols[2]:
    st.metric("IRR", '不适用' if best_scenario is None else format_percent(best_scenario['IRR']))
with metric_cols[3]:
    st.metric("动态回收期", '不适用' if best_scenario is None else format_years(best_scenario['动态回收期']))

tab_model, tab_results, tab_sensitivity, tab_validation = st.tabs([
    "模型说明",
    "计算结果",
    "敏感性分析",
    "验证模块"
])

with tab_model:
    st.subheader("模型口径")
    st.markdown("""
    本工具把每一个可选等待年限视为一个确定型投资方案。若选择等待 `w` 年后投资，
    投资成本先随等待年限增长，再折现回当前时点；投产后的每年现金流按其真实发生年份
    折现回当前时点。
    """)
    st.latex(r"NPV_w=-\frac{I_w}{(1+r)^w}+\sum_{k=1}^{n}\frac{CF_{w+k}}{(1+r)^{w+k}}")
    st.markdown("""
    判断规则：
    - 只比较市场窗口期内的有效方案。
    - 若最高 NPV 小于 0，则拒绝项目。
    - 若存在 NPV 非负方案，则推荐 NPV 最大的投资年份。
    - IRR、静态回收期和动态回收期用于辅助解释，不替代 NPV 主规则。
    """)

    if best_scenario is not None:
        st.subheader("最佳方案现金流")
        visualizer.plot_cash_flow_diagram(best_scenario['投资年份'], best_scenario['净现金流列表'])

with tab_results:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("NPV 曲线")
        visualizer.plot_npv_curve(results)
    with col2:
        st.subheader("投资时点分析")
        visualizer.plot_investment_timing(results)

    st.subheader("详细计算结果")
    display_rows = []
    for item in results:
        display_rows.append({
            '投资年份': item['投资年份'],
            '状态': '有效' if item['是否有效'] else item['无效原因'],
            'NPV（万元）': None if not item['是否有效'] else round(item['NPV'], 2),
            'IRR': format_percent(item['IRR']),
            '静态回收期': format_years(item['静态回收期']),
            '动态回收期': format_years(item['动态回收期']),
            '投资成本（万元）': round(item['投资成本'], 2),
            '成本现值（万元）': round(item['成本现值'], 2),
            '累计收益（万元）': round(item['累计收益'], 2),
            '收益增长率': format_percent(item['年收益率'])
        })
    st.dataframe(pd.DataFrame(display_rows), use_container_width=True)

    if current_scenario is not None and best_scenario is not None:
        st.info(
            f"立即投资 NPV 为 {current_scenario['NPV']:.2f} 万元；"
            f"推荐方案 NPV 为 {best_scenario['NPV']:.2f} 万元；"
            f"二者差额为 {recommendation['npv_difference']:.2f} 万元。"
        )

with tab_sensitivity:
    st.subheader("折现率敏感性分析")
    st.write("比较不同折现率下推荐投资年份是否发生变化。")

    candidate_rates = sorted({0.05, 0.08, 0.10, 0.12, 0.15, discount_rate / 100})
    sensitivity_rows = []
    for rate in candidate_rates:
        calc = InvestmentCalculator(
            current_investment_cost=current_investment_cost,
            current_annual_return=current_annual_return,
            future_growth_rate=future_growth_rate / 100,
            discount_rate=rate,
            project_lifetime=project_lifetime,
            max_wait_years=max_wait_years,
            cost_increase_rate=cost_increase_rate / 100,
            opportunity_loss_rate=opportunity_loss_rate / 100,
            growth_decline_rate=growth_decline_amount / 100,
            cost_increase_yearly_rate=cost_increase_yearly_rate / 100,
            market_window_years=market_window_years,
            early_bonus_rate=early_bonus_rate / 100
        )
        rate_recommendation = calc.get_recommendation()
        rate_best = rate_recommendation['best_scenario']
        if rate_best is None:
            continue
        sensitivity_rows.append({
            '折现率': f"{rate * 100:.1f}%",
            '最佳投资年份': rate_best['投资年份'],
            '最大NPV': round(rate_best['NPV'], 2),
            '推荐状态': rate_recommendation['status'],
            '推荐结论': rate_recommendation['decision']
        })

    sensitivity_df = pd.DataFrame(sensitivity_rows)
    st.dataframe(sensitivity_df, use_container_width=True)
    visualizer.plot_sensitivity_analysis(sensitivity_df)

with tab_validation:
    validator = InvestmentValidator()
    validator.run_validation()
