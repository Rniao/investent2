from typing import Dict, List, Optional


class InvestmentCalculator:
    """投资时机决策计算器。

    所有金额单位均为万元，所有利率在程序内部均使用小数形式。
    """

    def __init__(self, current_investment_cost: float, current_annual_return: float,
                 future_growth_rate: float, discount_rate: float, project_lifetime: int,
                 max_wait_years: int, cost_increase_rate: float, opportunity_loss_rate: float,
                 growth_decline_rate: float = 0.0, cost_increase_yearly_rate: float = 0.0,
                 market_window_years: int = 20, early_bonus_rate: float = 0.0):
        self.current_investment_cost = current_investment_cost
        self.current_annual_return = current_annual_return
        self.future_growth_rate = future_growth_rate
        self.discount_rate = discount_rate
        self.project_lifetime = int(project_lifetime)
        self.max_wait_years = int(max_wait_years)
        self.cost_increase_rate = cost_increase_rate
        self.opportunity_loss_rate = opportunity_loss_rate
        self.growth_decline_rate = growth_decline_rate
        self.cost_increase_yearly_rate = cost_increase_yearly_rate
        self.market_window_years = int(market_window_years)
        self.early_bonus_rate = early_bonus_rate

    @staticmethod
    def _safe_discount(value: float, rate: float, periods: int) -> float:
        if rate <= -1:
            raise ValueError("折现率必须大于 -100%。")
        return value / ((1 + rate) ** periods)

    @staticmethod
    def _calculate_payback(initial_cost: float, cash_flows: List[float]) -> Optional[float]:
        if initial_cost <= 0:
            return 0.0

        cumulative = -initial_cost
        for year, flow in enumerate(cash_flows, start=1):
            before = cumulative
            cumulative += flow
            if cumulative >= 0:
                if flow == 0:
                    return float(year)
                return (year - 1) + (-before / flow)
        return None

    @classmethod
    def _calculate_dynamic_payback(cls, initial_cost: float, cash_flows: List[float],
                                   discount_rate: float) -> Optional[float]:
        discounted_flows = [
            cls._safe_discount(flow, discount_rate, year)
            for year, flow in enumerate(cash_flows, start=1)
        ]
        return cls._calculate_payback(initial_cost, discounted_flows)

    @classmethod
    def _calculate_irr(cls, initial_cost: float, cash_flows: List[float]) -> Optional[float]:
        if initial_cost <= 0 or not cash_flows or sum(cash_flows) <= 0:
            return None

        def project_npv(rate: float) -> float:
            return -initial_cost + sum(
                cls._safe_discount(flow, rate, year)
                for year, flow in enumerate(cash_flows, start=1)
            )

        low = -0.9999
        high = 1.0
        low_value = project_npv(low)
        high_value = project_npv(high)

        while low_value * high_value > 0 and high < 10:
            high *= 2
            high_value = project_npv(high)

        if low_value * high_value > 0:
            return None

        for _ in range(100):
            mid = (low + high) / 2
            mid_value = project_npv(mid)
            if abs(mid_value) < 1e-7:
                return mid
            if low_value * mid_value <= 0:
                high = mid
                high_value = mid_value
            else:
                low = mid
                low_value = mid_value
        return (low + high) / 2

    def _calculate_effective_cost(self, investment_year: int) -> float:
        cost = self.current_investment_cost * ((1 + self.cost_increase_rate) ** investment_year)
        if self.cost_increase_yearly_rate > 0:
            cost *= (1 + self.cost_increase_yearly_rate) ** investment_year
        return cost

    def _calculate_effective_growth_rate(self, investment_year: int) -> float:
        growth_rate = self.future_growth_rate - self.growth_decline_rate * investment_year
        growth_rate = max(growth_rate, 0.0)
        if investment_year == 0 and self.early_bonus_rate > 0:
            growth_rate += self.early_bonus_rate
        return growth_rate

    def _calculate_cash_flows(self, investment_year: int, growth_rate: float) -> List[float]:
        opportunity_factor = max(0.0, 1 - self.opportunity_loss_rate * investment_year)
        cash_flows = []
        for operating_year in range(1, self.project_lifetime + 1):
            calendar_year = investment_year + operating_year
            market_adjusted_return = self.current_annual_return * ((1 + growth_rate) ** calendar_year)
            cash_flows.append(market_adjusted_return * opportunity_factor)
        return cash_flows

    def calculate_npv(self, investment_year: int) -> Dict:
        investment_year = int(investment_year)
        if investment_year > self.market_window_years:
            return {
                '投资年份': investment_year,
                '是否有效': False,
                '无效原因': '超过市场窗口期',
                'NPV': -float('inf'),
                'IRR': None,
                '静态回收期': None,
                '动态回收期': None,
                '累计收益': 0.0,
                '累计成本': 0.0,
                '投资成本': 0.0,
                '成本现值': 0.0,
                '年收益率': 0.0,
                '净现金流列表': [],
                '折现现金流列表': []
            }

        effective_cost = self._calculate_effective_cost(investment_year)
        cost_present_value = self._safe_discount(effective_cost, self.discount_rate, investment_year)
        effective_growth_rate = self._calculate_effective_growth_rate(investment_year)
        cash_flows = self._calculate_cash_flows(investment_year, effective_growth_rate)

        discounted_flows = [
            self._safe_discount(flow, self.discount_rate, investment_year + year)
            for year, flow in enumerate(cash_flows, start=1)
        ]
        npv = sum(discounted_flows) - cost_present_value

        return {
            '投资年份': investment_year,
            '是否有效': True,
            '无效原因': '',
            'NPV': npv,
            'IRR': self._calculate_irr(effective_cost, cash_flows),
            '静态回收期': self._calculate_payback(effective_cost, cash_flows),
            '动态回收期': self._calculate_dynamic_payback(
                effective_cost, cash_flows, self.discount_rate
            ),
            '累计收益': sum(cash_flows),
            '累计成本': effective_cost,
            '投资成本': effective_cost,
            '成本现值': cost_present_value,
            '年收益率': effective_growth_rate,
            '净现金流列表': cash_flows,
            '折现现金流列表': discounted_flows
        }

    def calculate_all_scenarios(self) -> List[Dict]:
        return [self.calculate_npv(year) for year in range(self.max_wait_years + 1)]

    def find_optimal_investment_year(self) -> int:
        recommendation = self.get_recommendation()
        best_scenario = recommendation.get('best_scenario')
        if not best_scenario:
            return 0
        return best_scenario['投资年份']

    def get_recommendation(self) -> Dict:
        results = self.calculate_all_scenarios()
        valid_results = [result for result in results if result['是否有效']]

        if not valid_results:
            return {
                'decision': '无法投资',
                'status': 'invalid',
                'best_scenario': None,
                'current_scenario': None,
                'npv_difference': None,
                'message': '所有候选投资年份均超过市场窗口期，当前参数下没有有效投资方案。'
            }

        best_scenario = max(valid_results, key=lambda result: result['NPV'])
        current_scenario = next(
            (result for result in valid_results if result['投资年份'] == 0),
            valid_results[0]
        )
        npv_difference = best_scenario['NPV'] - current_scenario['NPV']

        if best_scenario['NPV'] < 0:
            return {
                'decision': '不建议投资',
                'status': 'reject',
                'best_scenario': best_scenario,
                'current_scenario': current_scenario,
                'npv_difference': npv_difference,
                'message': (
                    f"所有有效方案的 NPV 均小于 0，最高 NPV 为 "
                    f"{best_scenario['NPV']:.2f} 万元，项目不能达到给定折现率要求。"
                )
            }

        if best_scenario['投资年份'] == 0:
            decision = '立即投资'
            message = (
                f"第0年投资的 NPV 最高，为 {best_scenario['NPV']:.2f} 万元，"
                "说明立即投资能够带来最大的现值收益。"
            )
        else:
            decision = f"等待 {best_scenario['投资年份']} 年后投资"
            message = (
                f"等待 {best_scenario['投资年份']} 年后投资的 NPV 最高，为 "
                f"{best_scenario['NPV']:.2f} 万元，比立即投资高 "
                f"{npv_difference:.2f} 万元。"
            )

        return {
            'decision': decision,
            'status': 'accept',
            'best_scenario': best_scenario,
            'current_scenario': current_scenario,
            'npv_difference': npv_difference,
            'message': message
        }
