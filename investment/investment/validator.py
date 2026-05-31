import streamlit as st

from calculator import InvestmentCalculator


class InvestmentValidator:
    def __init__(self):
        self.test_cases = [
            {
                'name': '基础案例：立即投资最优',
                'params': {
                    'current_investment_cost': 1000,
                    'current_annual_return': 200,
                    'future_growth_rate': 0.05,
                    'discount_rate': 0.08,
                    'project_lifetime': 10,
                    'max_wait_years': 5,
                    'cost_increase_rate': 0.03,
                    'opportunity_loss_rate': 0.02
                },
                'expected_year': 0,
                'expected_status': 'accept'
            },
            {
                'name': '拓展案例：等待2年最优',
                'params': {
                    'current_investment_cost': 500,
                    'current_annual_return': 100,
                    'future_growth_rate': 0.06,
                    'discount_rate': 0.05,
                    'project_lifetime': 6,
                    'max_wait_years': 5,
                    'cost_increase_rate': 0.01,
                    'opportunity_loss_rate': 0.0,
                    'growth_decline_rate': 0.005
                },
                'expected_year': 2,
                'expected_status': 'accept'
            },
            {
                'name': '拒绝案例：所有方案NPV为负',
                'params': {
                    'current_investment_cost': 1000,
                    'current_annual_return': 20,
                    'future_growth_rate': 0.01,
                    'discount_rate': 0.10,
                    'project_lifetime': 3,
                    'max_wait_years': 2,
                    'cost_increase_rate': 0.0,
                    'opportunity_loss_rate': 0.0
                },
                'expected_year': None,
                'expected_status': 'reject'
            },
            {
                'name': '约束案例：市场窗口期过滤',
                'params': {
                    'current_investment_cost': 1000,
                    'current_annual_return': 200,
                    'future_growth_rate': 0.05,
                    'discount_rate': 0.08,
                    'project_lifetime': 10,
                    'max_wait_years': 4,
                    'cost_increase_rate': 0.0,
                    'opportunity_loss_rate': 0.0,
                    'market_window_years': 2
            },
                'expected_year': 2,
                'expected_status': 'accept',
                'expected_invalid_years': [3, 4]
            }
        ]

    @staticmethod
    def _format_percent(value):
        if value is None:
            return '无法计算'
        return f'{value * 100:.2f}%'

    @staticmethod
    def _format_years(value):
        if value is None:
            return '未回收'
        return f'{value:.2f} 年'

    def validate_manual_calculation(self):
        st.subheader("手动验证案例")

        st.markdown("""
        选用基础案例进行手算校验。参数为：当前投资成本 1000 万元、当前年收益
        200 万元、收益增长率 5%、折现率 8%、项目寿命 10 年、等待成本上升率
        3%、机会损失率 2%。
        """)

        calculator = InvestmentCalculator(**self.test_cases[0]['params'])
        result_now = calculator.calculate_npv(0)
        result_wait = calculator.calculate_npv(1)

        st.write("**立即投资（第0年）**")
        st.latex(r"NPV_0=-1000+\sum_{k=1}^{10}\frac{200(1+5\%)^k}{(1+8\%)^k}")
        st.write(f"程序计算 NPV = {result_now['NPV']:.2f} 万元")

        st.write("**等待1年投资**")
        st.latex(
            r"NPV_1=-\frac{1000(1+3\%)}{1+8\%}+"
            r"\sum_{k=1}^{10}\frac{200(1+5\%)^{1+k}(1-2\%)}{(1+8\%)^{1+k}}"
        )
        st.write(f"程序计算 NPV = {result_wait['NPV']:.2f} 万元")

        if result_now['NPV'] > result_wait['NPV']:
            st.success("手算公式口径与程序输出一致：基础案例下立即投资优于等待1年。")
        else:
            st.error("验证失败：基础案例的程序输出与预期判断不一致。")

    def validate_all_test_cases(self):
        st.subheader("自动化测试案例")

        rows = []
        for test_case in self.test_cases:
            calculator = InvestmentCalculator(**test_case['params'])
            recommendation = calculator.get_recommendation()
            best_scenario = recommendation['best_scenario']
            best_year = best_scenario['投资年份'] if best_scenario else None
            results = calculator.calculate_all_scenarios()
            invalid_years = [item['投资年份'] for item in results if not item['是否有效']]

            status_ok = recommendation['status'] == test_case['expected_status']
            year_ok = (
                test_case['expected_year'] is None
                or best_year == test_case['expected_year']
            )
            invalid_ok = True
            if 'expected_invalid_years' in test_case:
                invalid_ok = invalid_years == test_case['expected_invalid_years']

            passed = status_ok and year_ok and invalid_ok
            rows.append({
                '测试案例': test_case['name'],
                '预期状态': test_case['expected_status'],
                '实际状态': recommendation['status'],
                '预期最佳年份': '不适用' if test_case['expected_year'] is None else f"第{test_case['expected_year']}年",
                '实际最佳年份': '不适用' if best_year is None else f"第{best_year}年",
                '最高NPV': '不适用' if best_scenario is None else f"{best_scenario['NPV']:.2f} 万元",
                '测试状态': '通过' if passed else '失败'
            })

        st.dataframe(rows, use_container_width=True)

        if all(row['测试状态'] == '通过' for row in rows):
            st.success("所有验证案例均通过。")
        else:
            st.error("存在验证失败案例，请检查计算公式或参数设置。")

    def validate_metric_example(self):
        st.subheader("IRR与回收期验证")

        calculator = InvestmentCalculator(
            current_investment_cost=100,
            current_annual_return=40,
            future_growth_rate=0.0,
            discount_rate=0.10,
            project_lifetime=4,
            max_wait_years=0,
            cost_increase_rate=0.0,
            opportunity_loss_rate=0.0
        )
        result = calculator.calculate_npv(0)

        st.write("验证现金流：第0年投入 100 万元，未来4年每年回收 40 万元。")
        st.write(f"IRR = {self._format_percent(result['IRR'])}")
        st.write(f"静态回收期 = {self._format_years(result['静态回收期'])}")
        st.write(f"动态回收期 = {self._format_years(result['动态回收期'])}")
        st.info("该案例可用 Excel 的 IRR 函数和累计现金流表进行对比验证。")

    def run_validation(self):
        st.write("验证模块用于检查公式口径、推荐规则和关键课程指标是否正确。")

        tab1, tab2, tab3 = st.tabs(["手动验证", "自动化测试", "IRR与回收期"])

        with tab1:
            self.validate_manual_calculation()

        with tab2:
            self.validate_all_test_cases()

        with tab3:
            self.validate_metric_example()
