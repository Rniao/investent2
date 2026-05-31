import math
import unittest

try:
    from .calculator import InvestmentCalculator
except ImportError:
    from calculator import InvestmentCalculator


class InvestmentCalculatorTest(unittest.TestCase):
    def test_immediate_investment_is_optimal(self):
        calculator = InvestmentCalculator(
            current_investment_cost=1000,
            current_annual_return=200,
            future_growth_rate=0.05,
            discount_rate=0.08,
            project_lifetime=10,
            max_wait_years=5,
            cost_increase_rate=0.03,
            opportunity_loss_rate=0.02
        )

        recommendation = calculator.get_recommendation()

        self.assertEqual(recommendation['status'], 'accept')
        self.assertEqual(recommendation['best_scenario']['投资年份'], 0)
        self.assertEqual(recommendation['decision'], '立即投资')
        self.assertAlmostEqual(recommendation['best_scenario']['NPV'], 718.55, places=2)

    def test_waiting_investment_can_be_optimal(self):
        calculator = InvestmentCalculator(
            current_investment_cost=500,
            current_annual_return=100,
            future_growth_rate=0.06,
            discount_rate=0.05,
            project_lifetime=6,
            max_wait_years=5,
            cost_increase_rate=0.01,
            opportunity_loss_rate=0.0,
            growth_decline_rate=0.005
        )

        recommendation = calculator.get_recommendation()

        self.assertEqual(recommendation['status'], 'accept')
        self.assertEqual(recommendation['best_scenario']['投资年份'], 2)
        self.assertIn('等待 2 年后投资', recommendation['decision'])
        self.assertGreater(recommendation['best_scenario']['NPV'], recommendation['current_scenario']['NPV'])

    def test_rejects_project_when_all_npvs_are_negative(self):
        calculator = InvestmentCalculator(
            current_investment_cost=1000,
            current_annual_return=20,
            future_growth_rate=0.01,
            discount_rate=0.10,
            project_lifetime=3,
            max_wait_years=2,
            cost_increase_rate=0.0,
            opportunity_loss_rate=0.0
        )

        recommendation = calculator.get_recommendation()

        self.assertEqual(recommendation['status'], 'reject')
        self.assertEqual(recommendation['decision'], '不建议投资')
        self.assertLess(recommendation['best_scenario']['NPV'], 0)

    def test_market_window_filters_invalid_years(self):
        calculator = InvestmentCalculator(
            current_investment_cost=1000,
            current_annual_return=200,
            future_growth_rate=0.05,
            discount_rate=0.08,
            project_lifetime=10,
            max_wait_years=4,
            cost_increase_rate=0.0,
            opportunity_loss_rate=0.0,
            market_window_years=2
        )

        results = calculator.calculate_all_scenarios()

        self.assertTrue(results[2]['是否有效'])
        self.assertFalse(results[3]['是否有效'])
        self.assertFalse(results[4]['是否有效'])
        self.assertEqual(results[3]['无效原因'], '超过市场窗口期')
        self.assertTrue(math.isinf(results[3]['NPV']))

    def test_irr_and_payback_metrics(self):
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

        self.assertAlmostEqual(result['IRR'], 0.2186, places=4)
        self.assertAlmostEqual(result['静态回收期'], 2.5, places=2)
        self.assertAlmostEqual(result['动态回收期'], 3.02, places=2)
        self.assertEqual(result['净现金流列表'], [40.0, 40.0, 40.0, 40.0])


if __name__ == '__main__':
    unittest.main()
