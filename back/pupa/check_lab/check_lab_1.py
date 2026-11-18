import math
from rapidfuzz.distance import Levenshtein

pi = math.pi
error = 0.05

student = {2: 12.71, 3: 4.30, 4: 3.18, 5: 2.77}


def close(exp: float, res: float, rel: float = error, abs_tol: float = 0.0) -> bool:
    return abs(res - exp) <= max(rel * abs(exp), abs_tol)


def compare_err(exp: float, res: float, err: float = error) -> bool:
    return close(exp, res, rel=err)


# 1.Расшифровка обозначений

defs = {
    "<p>": {"плотность", "плотность образца", "плотность материала"},
    "<d>": {"диаметр", "диаметр образца"},
    "m": {"масса", "масса образца"},
    "<h>": {"высота", "высота образца"},
}


def _norm(s: str) -> str:
    return " ".join(s.lower().replace("ё", "е").split())


def check_definition(answer: str, key: str) -> bool:
    """допускается 1 опечатка в ответе."""
    a = _norm(answer)
    return any(Levenshtein.distance(a, _norm(v)) <= 1 for v in defs[key])


def check_definitions(answers: dict) -> dict:
    return {k: check_definition(answers.get(k, ""), k) for k in defs}


# 2. Средства измерений

def _unit(u):
    """Приводит един измерения к норме"""
    return u.strip().rstrip(".").strip().lower()


def _intervals(x):
    """300 -> [(300, 300)]; (120, 250) -> [(120, 250)];"""
    if isinstance(x, tuple):
        return [x]
    if isinstance(x, list):
        return [i if isinstance(i, tuple) else (i, i) for i in x]
    return [(x, x)]


class measure_instrument:
    def __init__(self, id, name, range, range_units, scale, scale_units, limit, limit_units):
        self.id = id
        self.name = name
        self.range = range
        self.range_units = range_units
        self.scale = scale
        self.scale_units = scale_units
        self.limit = limit
        self.limit_units = limit_units

    def same_name(self, name):
        return Levenshtein.distance(_norm(self.name), _norm(name)) <= 1


    def check(self, student):
        """"Сравнивает строку студента с эталоном"""
        def ok(field):
            """"Проверка попадания в интервал"""
            v = getattr(student, field)
            return any(lo - 1e-9 <= v <= hi + 1e-9
                       for lo, hi in _intervals(getattr(self, field)))

        return {
            "name": self.same_name(student.name),
            "range": ok("range"),
            "range_units": _unit(student.range_units) == _unit(self.range_units),
            "scale": ok("scale"),
            "scale_units": _unit(student.scale_units) == _unit(self.scale_units),
            "limit": ok("limit"),
            "limit_units": _unit(student.limit_units) == _unit(self.limit_units),
        }


instruments = [
    measure_instrument(1, "Весы электронные цифровые ВК-300", 300, "г.", 0.01, "г.", 0.005, "г."),
    measure_instrument(2, "Весы электронные цифровые ВК-300", 300, "г.", 0.01, "г.", 0.01, "г."),
    measure_instrument(3, "Весы электронные цифровые ВЭУ-200", 200, "г.", 0.002, "г.", 0.005, "г."),
    measure_instrument(4, "Микрометр", 25, "мм.", 0.01, "мм.", 0.004, "мм."),
    measure_instrument(5, "Штангенциркуль", (120, 250), "мм.", (0.02, 0.1), "мм.", (0.02, 0.1), "мм."),
    measure_instrument(6, "Весы электронные цифровые", 500, "г.", 0.001, "г.", 0.001, "г."),
]


def check_instrument(student):
    refs = [r for r in instruments if r.same_name(student.name)]
    if not refs:
        return {"name": False}
    return max((r.check(student) for r in refs), key=lambda res: sum(res.values()))

def kind_of(student):
    """"Определение типа прибора"""
    n = _norm(student.name)
    if n.startswith("весы"):
        return "balance"
    if n.startswith("микрометр"):
        return "micrometer"
    if n.startswith("штангенциркуль"):
        return "caliper"
    return None


def check_instruments(ls):
    """Окончательная проверка"""
    return {
        "rows": [check_instrument(s) for s in ls],
        "set_ok": sorted(kind_of(s) or "" for s in ls) == ["balance", "caliper", "micrometer"],
    }


def get_instrument(ls, kind):
    return next((s for s in ls if kind_of(s) == kind), None)


SAMPLES = {
    1: (39.95, 8.13, 16.49, "железо"),
    2: (37.77, 9.80, 7.88, "алюминий"),
    5: (61.45, 9.47, 12.42, "алюминий"),
    9: (34.40, 8.62, 17.748, "медь"),
    11: (22.90, 12.90, 27.23, "медь"),
    12: (21.10, 13.10, 24.88, "медь"),
    13: (63.18, 13.80, 84.74, "медь"),
    14: (53.10, 11.07, 23.65, "титан"),
    17: (50.80, 10.95, 22.222, "титан"),
    24: (42.90, 9.80, 25.18, "сталь"),
    26: (63.00, 10.33, 41.512, "сталь"),
    27: (30.20, 15.95, 47.30, "сталь"),
    29: (30.20, 15.95, 47.30, "сталь"),
    31: (60.25, 11.00, 44.958, "сталь"),
    35: (54.50, 12.30, 50.436, "сталь"),
    47: (50.20, 11.35, 37.18, "сплав"),
    48: (50.00, 11.40, 39.774, "сталь"),
    52: (49.90, 11.18, 36.874, "сплав"),
    59: (37.90, 11.58, 32.89, "латунь"),
    64: (54.00, 14.30, 38.58, "титан"),
}

def check_sample_number(num: int) -> bool:
    return num in SAMPLES

# 3. Проверка массы
def expected_delta_m(theta_osn: float, scale: float) -> float:
    return 1.1 * math.sqrt(theta_osn**2 + (scale / 2) ** 2)


def check_mass(m: float, delta_m: float, sample_num: int, table: list) -> dict:
    """
    m, delta_m — вписано студентом в пункте 3.1
    sample_num — «Образец №»
    table      — список measure_instrument из пункта 2
    """
    balance = get_instrument(table, "balance")
    res = {
        "sample": check_sample_number(sample_num),
        "balance_found": balance is not None,
        "m": False,
        "delta_m": False,
    }
    if res["sample"]:
        res["m"] = close(SAMPLES[sample_num][2], m)
    if balance is not None:
        res["delta_m"] = close(expected_delta_m(balance.limit, balance.scale), delta_m)
    return res



# 4. Проверка диаметра и высоты

def check_series(values: list, entered: dict, ref_mean: float, theta_expected: float,
                 scale: float, max_dev: float = 0.05) -> tuple:
    """
    values   — d_i (или h_i), введённые студентом
    entered  — то, что студент вписал: devs, sqs, mean, sum_sq, S, eps, theta, delta,
               res_mean, res_delta
    ref_mean — <d> или <h> образца из приложения
    theta_expected — θосн прибора (из таблицы студента)
    scale    — цена деления прибора (для допуска на округление)
    max_dev  — |x_i - <x>| не должно превышать max_dev * <x>
               (в 1.xlsx для d и h — 0,05; в 1_with_data.xlsx для d написано 0,01 — уточнить)
    Возвращает (checks, expected).
    """
    n = len(values)
    mean = sum(values) / n
    devs = [v - mean for v in values]
    sqs = [d * d for d in devs]
    sum_sq = sum(sqs)
    S = math.sqrt(sum_sq / (n * (n - 1))) if n > 1 else float("nan")
    eps = student.get(n, float("nan")) * S
    delta = math.sqrt(eps**2 + theta_expected**2)

    expected = {"mean": mean, "devs": devs, "sqs": sqs, "sum_sq": sum_sq,
                "S": S, "eps": eps, "theta": theta_expected, "delta": delta}

    checks = {
        "n_ok": n in student,
        "spread_ok": all(abs(d) <= max_dev * mean for d in devs),
        "not_all_equal": sum_sq > 0,
        "mean_vs_sample": close(ref_mean, entered["mean"]),
        "mean": close(mean, entered["mean"], rel=0.001),
        "devs": len(entered["devs"]) == n
        and all(close(e, s, abs_tol=scale) for e, s in zip(devs, entered["devs"])),
        "sqs": len(entered["sqs"]) == n
        and all(close(e, s, abs_tol=scale**2) for e, s in zip(sqs, entered["sqs"])),
        "sum_sq": close(sum_sq, entered["sum_sq"], abs_tol=scale**2),
        "S": close(S, entered["S"]),
        "eps": close(eps, entered["eps"]),
        "theta": close(theta_expected, entered["theta"], rel=1e-6),
        "delta": close(delta, entered["delta"]),
        "res_mean": close(mean, entered["res_mean"], rel=0.001),
        "res_delta": close(delta, entered["res_delta"]),
    }
    return checks, expected


# 5. Проверка плотности

def expected_density(m_g: float, d_mm: float, h_mm: float) -> float:
    """m в граммах, d и h в мм -> кг/м³."""
    return 4 * m_g * 1e6 / (pi * d_mm**2 * h_mm)


def expected_gamma(m, dm, d, dd, h, dh) -> float:
    return math.sqrt((dm / m) ** 2 + (2 * dd / d) ** 2 + (dh / h) ** 2)


def round_sig(x: float, n: int = 1) -> float:
    """Округление до n значащих цифр"""
    if x == 0:
        return 0.0
    return round(x, n - 1 - math.floor(math.log10(abs(x))))


def expected_final(rho: float, delta_rho: float) -> tuple:
    """Δρ — до первой значащей цифры, ρ — до того же разряда."""
    digits = 0 - math.floor(math.log10(abs(delta_rho)))
    return round(rho, digits), round(delta_rho, digits)


def check_density_block(entered: dict, m, dm, d, dd, h, dh) -> dict:
    """
    entered = {"rho", "gamma", "delta_rho", "final_rho", "final_delta"}
    m, dm, d, dd, h, dh — значения студента из пунктов 3.1–3.3.
    """
    rho = expected_density(m, d, h)
    gamma = expected_gamma(m, dm, d, dd, h, dh)
    delta_rho = gamma * rho
    final_rho, final_delta = expected_final(rho, delta_rho)
    return {
        "rho": close(rho, entered["rho"]),
        "gamma": close(gamma, entered["gamma"]),
        "delta_rho": close(delta_rho, entered["delta_rho"]),
        "final_rounding": entered["final_rho"] == final_rho and entered["final_delta"] == final_delta,
    }



# 6. Проверка выводов - LLM
def check_conclusion(text: str):
    return None

