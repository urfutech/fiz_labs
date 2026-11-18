#python -m unittest tests_lab_1 -v - проверка всех тестов сразу

import math
import unittest

try:
    from .check_lab_1 import *  # noqa: F401,F403  (запуск как пакет)
except ImportError:
    from check_lab_1 import *  # noqa: F401,F403  (запуск из папки: python -m unittest)

# Эталонный отчёт: 1_with_data.xlsx, образец № 27
D = [15.94, 15.93, 15.92, 15.93, 15.91]
H = [30.0, 30.05, 30.1, 30.1, 30.05]
M = 47.27

#Пример идеального студента, который заполнил отчет без ошибок
def good_entered(values, theta, delta, mean, scale):
    n = len(values)
    devs = [v - mean for v in values]
    sqs = [x * x for x in devs]
    S = math.sqrt(sum(sqs) / (n * (n - 1)))
    eps = student[n] * S
    return dict(devs=devs, sqs=sqs, mean=mean, sum_sq=sum(sqs), S=S, eps=eps,
                theta=theta, delta=delta, res_mean=mean, res_delta=delta)

#Проверка на совпадение названий
class TestDefinition(unittest.TestCase):
    def test_exact(self):
        self.assertTrue(check_definition("Плотность", "<p>"))

    def test_one_typo(self):
        self.assertTrue(check_definition("плотнасть образца", "<p>"))

    def test_wrong(self):
        self.assertFalse(check_definition("объём", "<p>"))

    def test_extra_spaces_and_case(self):
        self.assertTrue(check_definition("  ДИАМЕТР  образца ", "<d>"))


Inst = measure_instrument


def student_table():
    return [
        Inst(None, "Весы электронные цифровые ВК-300", 300, "г.", 0.01, "г.", 0.005, "г."),
        Inst(None, "Микрометр", 25, "мм.", 0.01, "мм.", 0.004, "мм."),
        Inst(None, "Штангенциркуль", 250, "мм.", 0.05, "мм.", 0.05, "мм."),
    ]

# Проверка параметров приборов на совпадение
class TestInstruments(unittest.TestCase):
    def test_all_ok(self):
        res = check_instruments(student_table())
        self.assertTrue(res["set_ok"])
        for r in res["rows"]:
            self.assertTrue(all(r.values()), r)

    def test_order_does_not_matter(self):
        res = check_instruments(list(reversed(student_table())))
        self.assertTrue(res["set_ok"])
        self.assertTrue(all(all(r.values()) for r in res["rows"]))

    def test_dot_after_unit_optional(self):
        row = Inst(None, "Микрометр", 25, "мм", 0.01, "мм", 0.004, "мм")
        self.assertTrue(all(check_instrument(row).values()))

    def test_name_with_typo_and_space(self):
        row = Inst(None, " Микрометер ", 25, "мм.", 0.01, "мм.", 0.004, "мм.")
        self.assertTrue(check_instrument(row)["name"])

    def test_wrong_limit(self):
        row = Inst(None, "Микрометр", 25, "мм.", 0.01, "мм.", 0.01, "мм.")
        self.assertFalse(check_instrument(row)["limit"])

    def test_wrong_units(self):
        row = Inst(None, "Микрометр", 25, "см.", 0.01, "мм.", 0.004, "мм.")
        self.assertFalse(check_instrument(row)["range_units"])

    def test_caliper_interval(self):
        row = Inst(None, "Штангенциркуль", 250, "мм.", 0.5, "мм.", 0.05, "мм.")
        self.assertFalse(check_instrument(row)["scale"])

    def test_balance_both_limits_allowed(self):
        for lim in (0.005, 0.01):
            row = Inst(None, "Весы электронные цифровые ВК-300", 300, "г.", 0.01, "г.", lim, "г.")
            self.assertTrue(all(check_instrument(row).values()))

    def test_unknown_instrument(self):
        self.assertEqual(check_instrument(Inst(None, "Линейка", 30, "см", 0.1, "см", 0.1, "см")),
                         {"name": False})

    def test_missing_instrument(self):
        self.assertFalse(check_instruments(student_table()[:2])["set_ok"])

    def test_get_instrument(self):
        self.assertAlmostEqual(get_instrument(student_table(), "balance").limit, 0.005)
        self.assertIsNone(get_instrument(student_table()[:2], "caliper"))

#Проверка массы по всем формулам
class TestMass(unittest.TestCase):
    def test_delta_formula(self):
        self.assertAlmostEqual(expected_delta_m(0.005, 0.01), 7.7781745930520238e-3)

    def test_mass_ok(self):
        r = check_mass(47.27, 7.7781745930520238e-3, 27, student_table())
        self.assertTrue(all(r.values()), r)

    def test_balance_order_irrelevant(self):
        r = check_mass(47.27, 7.7781745930520238e-3, 27, list(reversed(student_table())))
        self.assertTrue(all(r.values()), r)

    def test_other_balance_limit(self):
        # студент выбрал ВК-300 с пределом 0,01 — Δm должно считаться от его значения
        t = student_table()
        t[0].limit = 0.01
        dm = expected_delta_m(0.01, 0.01)
        self.assertTrue(check_mass(47.27, dm, 27, t)["delta_m"])
        self.assertFalse(check_mass(47.27, 7.7781745930520238e-3, 27, t)["delta_m"])

    def test_old_formula_is_wrong(self):
        # старая формула 1.1*(limit² + scale²) без sqrt и без /2
        wrong = 1.1 * (0.005**2 + 0.01**2)
        self.assertFalse(check_mass(47.27, wrong, 27, student_table())["delta_m"])

    def test_wrong_mass(self):
        self.assertFalse(check_mass(60.0, 7.7781745930520238e-3, 27, student_table())["m"])

    def test_unknown_sample(self):
        r = check_mass(47.27, 7.7781745930520238e-3, 99, student_table())
        self.assertFalse(r["sample"])
        self.assertFalse(r["m"])

    def test_no_balance_in_table(self):
        r = check_mass(47.27, 7.7781745930520238e-3, 27, student_table()[1:])
        self.assertFalse(r["balance_found"])
        self.assertFalse(r["delta_m"])

# Проверка диаметра и высоты
class TestSeries(unittest.TestCase):
    def test_diameter_ok(self):
        entered = good_entered(D, 0.004, 1.4679761578445048e-2, 15.926, 0.01)
        checks, _ = check_series(D, entered, SAMPLES[27][1], 0.004, 0.01)
        self.assertTrue(all(checks.values()), checks)

    def test_height_ok(self):
        entered = good_entered(H, 0.05, 7.2010520064779954e-2, 30.06, 0.05)
        checks, _ = check_series(H, entered, SAMPLES[27][0], 0.05, 0.05)
        self.assertTrue(all(checks.values()), checks)

    def test_all_equal_measurements(self):
        vals = [15.9] * 5
        entered = good_entered(vals, 0.004, 0.004, 15.9, 0.01)
        checks, _ = check_series(vals, entered, 15.95, 0.004, 0.01)
        self.assertFalse(checks["not_all_equal"])

    def test_mean_far_from_sample(self):
        vals = [10.0, 10.01, 10.0, 10.02, 10.01]
        entered = good_entered(vals, 0.004, 0.01, sum(vals) / 5, 0.01)
        checks, _ = check_series(vals, entered, SAMPLES[27][1], 0.004, 0.01)
        self.assertFalse(checks["mean_vs_sample"])

    def test_wrong_student_coef(self):
        entered = good_entered(D, 0.004, 1.4679761578445048e-2, 15.926, 0.01)
        entered["eps"] *= 1.5
        checks, _ = check_series(D, entered, SAMPLES[27][1], 0.004, 0.01)
        self.assertFalse(checks["eps"])

    def test_outlier_breaks_spread(self):
        vals = [15.94, 15.93, 15.92, 15.93, 17.5]
        mean = sum(vals) / 5
        entered = good_entered(vals, 0.004, 0.5, mean, 0.01)
        checks, _ = check_series(vals, entered, 15.95, 0.004, 0.01)
        self.assertFalse(checks["spread_ok"])


# Вычисляем плотность и её погрешности
class TestDensity(unittest.TestCase):
    dm, dd, dh = 7.7781745930520238e-3, 1.4679761578445048e-2, 7.2010520064779954e-2
    d, h = 15.926, 30.06

    def test_density_value(self):
        self.assertAlmostEqual(expected_density(M, self.d, self.h), 7893.93, places=1)

    def test_gamma_value(self):
        self.assertAlmostEqual(expected_gamma(M, self.dm, self.d, self.dd, self.h, self.dh),
                               3.0272529452020371e-3)

    def test_rounding(self):
        self.assertEqual(round_sig(13.65), 10.0)
        self.assertEqual(expected_final(4508.9, 13.65), (4510.0, 10.0))
        self.assertEqual(expected_final(7893.93, 23.9), (7890.0, 20.0))

    def test_block_ok(self):
        rho = expected_density(M, self.d, self.h)
        g = expected_gamma(M, self.dm, self.d, self.dd, self.h, self.dh)
        entered = dict(rho=rho, gamma=g, delta_rho=g * rho, final_rho=7890, final_delta=20)
        r = check_density_block(entered, M, self.dm, self.d, self.dd, self.h, self.dh)
        self.assertTrue(all(r.values()), r)

    def test_bad_rounding(self):
        rho = expected_density(M, self.d, self.h)
        g = expected_gamma(M, self.dm, self.d, self.dd, self.h, self.dh)
        entered = dict(rho=rho, gamma=g, delta_rho=g * rho, final_rho=7894, final_delta=23.9)
        r = check_density_block(entered, M, self.dm, self.d, self.dd, self.h, self.dh)
        self.assertFalse(r["final_rounding"])


if __name__ == "__main__":
    unittest.main()