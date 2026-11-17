from rapidfuzz.distance import Levenshtein

defs = {
    "<p>": {"плотность", "плотность образца", "плотность материала"},
    "<d>": {"диаметр", "диаметр образца"},
    "m": {"масса", "масса образца"},
    "<h>": {"высота", "высота образца"},
}

sample = {
    "<m>": None,
    "<d>": None,
    "<h>": None,
    "<p>": None,
}

inst = []

search_d = []
search_h = []


def compare_err(exp: float, res: float, err: float = 0.05):
    return exp * (1 - err) <= res and res <= exp * (1 + err)


def check_definition(inp: dict, defs: dict) -> bool:
    n = inp.count()
    correct = [False] * n
    for i in range(n):
        for j in range(defs.count()):
            if Levenshtein.dist(inp[i], defs[j]) <= 1:
                correct[i] = True
                break
    return correct


class measure_instrument:
    def __init__(
        self, id, name, range, range_units, scale, scale_units, limit, limit_units
    ):
        self.id = id
        self.name = name
        self.range = range
        self.range_units = range_units
        self.scale = scale
        self.scale_units = scale_units
        self.limit = limit
        self.limit_units = limit_units


instruments = [
    measure_instrument(
        id=1,
        name="Весы электронные цифровые ВК-300",
        range=300,
        range_units="г.",
        scale=0.01,
        scale_units="г.",
        limit=0.005,
        limit_units="г.",
    ),
    measure_instrument(
        id=2,
        name="Весы электронные цифровые ВК-300",
        range=300,
        range_units="г.",
        scale=0.01,
        scale_units="г.",
        limit=0.01,
        limit_units="г.",
    ),
    measure_instrument(
        id=3,
        name="Весы электронные цифровые ВЭУ-200",
        range=200,
        range_units="г.",
        scale=0.002,
        scale_units="г.",
        limit=0.005,
        limit_units="г.",
    ),
    measure_instrument(
        id=4,
        name="Микрометр",
        range=25,
        range_units="мм.",
        scale=0.01,
        scale_units="мм.",
        limit=0.004,
        limit_units="мм.",
    ),
    measure_instrument(
        id=5,
        name="Штангенциркуль",
        range=120,
        range_units="мм.",
        scale=0.1,
        scale_units="мм.",
        limit=0.1,
        limit_units="мм.",
    ),
]


def check_instruments(ls: [measure_instrument]):
    correct = [True] * len(ls)
    global inst
    inst = ls
    for i in range(len(ls)):
        for j in range(len(instruments)):
            if ls[i].id == instruments[j].id:
                if (
                    ls[i].name != instruments[j].name
                    or ls[i].range != instruments[j].range
                    or ls[i].range_units != instruments[j].range_units
                    or ls[i].scale != instruments[j].scale
                    or ls[i].scale_units != instruments[j].scale_units
                    or ls[i].limit != instruments[j].limit
                    or ls[i].limit_units != instruments[j].limit_units
                ):
                    correct[i] = False
    return correct


def check_mass(m: int, x: float = 0.05):
    delta = 1.1 * (inst[0].limit ** 2 + inst[0].scale ** 2)
    return delta * (1 - x) <= m and m <= delta * (1 + x)


class sample:
    def __init__(self, num, h, d, m, material):
        self.num = num
        self.h = h
        self.d = d
        self.m = m
        self.material = material


samples = [sample(9, 34.40, 8.62, 17.748, "медь")]
curr_samp = 0


def get_sample(num: int):
    global curr_samp
    curr_samp = num


sum_d = 0


class diametr:
    di: float
    di_d: float
    di_d_2: float


def check_diametr_correctness(ls: [diametr]):
    correct = [True] * len(ls)
    global search_d
    search_d = ls
    for i in range(len(ls)):
        if (
            ls[i].di * 0.05 > ls[i].di_i
            and ls[i].di_d_2 == 0
            and ls[i].d not in samples
        ):
            correct[i] = False
    return correct


def check_diametr(st_sum_d: float, st_d_: float, x: float = 0.05):
    global sum_d, _d_, samples
    sum_d = sum(samples[i].di_d_2 for i in range(len(samples)))
    return (
        sum_d * (1 - x) <= st_sum_d and st_sum_d <= sum_d * 1(1 + x),
        st_d_ == samples[curr_samp],
    )


err_2 = 0
n = len(search_d)


def check_err_2(s: float, x: float = 0.05):
    global err_2
    err_2 = sum_d / (n * (n - 1))
    return compare_err(err_2, s)


stud_coef = [0, 0, 12.71, 4.3, 3.188, 2.77]
rand_err = 0


def check_rand_err(err: float):
    global rand_err
    rand_err = sum_d * stud_coef[n]
    return compare_err(rand_err, err)

no_err = 0

def check_no_err(err: float):
    global no_err
    no_err = 
    return compare_err(rand_err, err)
