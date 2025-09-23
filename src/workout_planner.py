from src.parse_user_input import ParseInput
from src.sql_backend import fetch_by_block, DB_PATH, fetch_by_muscles_quota
from collections import defaultdict
import random

PUSH = {"chest", "triceps", "front delts", "side delts"}
PULL = {"biceps", "lats", "middle_back", "lower_back", "rear delts"}
LEGS = {"quadriceps", "hamstrings", "glutes", "calves", "abductors", "adductors"}
CORE = {"abdominals", "lower_back"}
BLOCK_SPLITS = {"push", "pull", "legs", "upper", "lower", "full"}

DEFAULT_SPLITS = {
    2: ["upper", "rest", "rest", "lower", "rest", "rest", "rest"],
    3: {
        "beginner": ["push", "rest", "pull", "rest", "legs", "rest", "rest"],
        "intermediate": ["chest_triceps", "rest", "back_biceps", "rest", "legs_shoulders", "rest", "rest"],
        "expert": ["chest_triceps", "rest", "back_biceps", "rest", "legs_shoulders", "rest", "rest"]
    },
    4: {
        "beginner": ["push", "pull", "legs", "full"],
        "intermediate": ["chest_triceps", "rest", "back_biceps", "rest", "shoulders", "legs", "rest"],
        "expert": ["chest_triceps", "rest", "back_biceps", "rest", "shoulders", "legs", "rest"]
    },
    5: {
        "beginner": ["push", "pull", "legs", "upper", "lower"],
        "intermediate": ["chest_triceps", "back_shoulders", "rest",  "chest_biceps", "legs", "back_arms", "rest"],
        "expert": ["chest_triceps", "back_shoulders", "rest",  "chest_biceps", "legs", "back_arms", "rest"]
    },
    6: {
        "beginner":     ["push", "pull", "legs", "push", "pull", "legs"],
        "intermediate": ["chest_triceps", "back_biceps", "legs", "shoulders", "rest", "upper", "lower"],
        "expert":       ["chest_triceps", "back_biceps", "legs", "shoulders", "rest", "upper", "lower"],
    },
    7: {
        "beginner":     ["push", "pull", "legs", "push", "pull", "legs", "full"],
        "intermediate": ["chest_triceps", "back_biceps", "legs", "shoulders", "upper", "lower", "full"],
        "expert":       ["chest_triceps", "back_biceps", "legs", "shoulders", "upper", "lower", "full"],
    },
}

COMBO_GROUPS = {
    "chest_triceps":   ["chest", "triceps"],
    "back_arms":       ["lats", "middle_back", "lower_back", "biceps", "triceps"],
    "back_biceps":     ["lats", "middle_back", "lower_back", "traps", "biceps", "forearms"],
    "legs_shoulders":  ["quadriceps", "hamstrings", "glutes", "calves", "front delts", "side delts", "rear delts"],
    "chest_shoulders": ["chest", "front delts", "side delts", "rear delts", "triceps"],
    "back_traps":      ["lats", "middle_back", "lower_back", "traps"],
    "back_rear_delts": ["lats", "middle_back", "lower_back", "rear delts", "traps"],
    "arms":            ["biceps", "triceps", "forearms"],
    "chest_biceps":    ["chest", "biceps"],
    "back_triceps":    ["lats", "middle_back", "triceps"],
    "shoulders":       ["front delts", "side delts", "rear delts"],
    "back_shoulders":  ["lats", "middle_back", "front delts", "side delts", "rear delts", "traps"],
    "legs":            ["quadriceps", "hamstrings", "glutes", "calves", "abductors", "adductors"],
    "legs_arms":       ["quadriceps", "hamstrings", "glutes", "biceps", "triceps"],
    "upper": ["chest","front delts", "side delts", "rear delts","triceps","biceps","lats","middle_back","traps","forearms"],
    "lower": ["quadriceps","hamstrings","glutes","calves","abductors","adductors"],
    "push":  ["chest","front delts", "side delts","triceps"],
    "pull":  ["lats","middle_back","lower_back","biceps","traps","forearms"],
    "full":  ["chest","triceps","front delts", "side delts", "rear delts","biceps","lats","middle_back","lower_back","traps",
              "forearms","quadriceps","hamstrings","glutes","calves","abductors","adductors","abdominals"],
}

MUSCLES_FOR_BLOCK = {
    "push":  ["chest","front delts","side delts","triceps"],
    "pull":  ["lats","middle_back","lower_back","rear delts","biceps","forearms","traps"],
    "legs":  ["quadriceps","hamstrings","glutes","calves","abductors","adductors"],
    "upper": ["chest","front delts","side delts","rear delts","triceps","biceps","lats","middle_back","traps","forearms"],
    "lower": ["quadriceps","hamstrings","glutes","calves","abductors","adductors"],
    "full":  ["chest","triceps","front delts","side delts","rear delts","biceps","lats","middle_back","lower_back",
              "traps","forearms","quadriceps","hamstrings","glutes","calves","abductors","adductors","abdominals"],
}

MUSCLE_QUOTAS = {
    "chest": (3, 5),
    "lats": (3, 5), "middle_back": (2, 4), "lower_back": (1, 2),
    "quadriceps": (3, 5), "hamstrings": (3, 5), "glutes": (2, 4),

    "biceps": (3, 4), "triceps": (3, 4),

    "traps": (1, 2), "rear delts": (1, 2), "forearms": (1, 2),
    "calves": (1, 2), "abductors": (1, 2), "adductors": (1, 2),
    "abdominals": (1, 2),
    "front delts": (2,3), "side delts": (2,3),
                                 
    "_default": (1, 2),
}

def _enforce_quotas(candidates, muscles, quotas, fill_to_max=True):
    # bucket by muscle, de-dupe
    by_m = defaultdict(list)
    seen = set()
    for ex in candidates:
        exid = ex.get("id")
        if exid in seen:
            continue
        seen.add(exid)
        by_m[ex.get("muscle")].append(ex)
    for m in by_m: random.shuffle(by_m[m])

    picks = []

    # 1) take minimums
    for m in muscles:
        mn, mx = quotas.get(m, quotas["_default"])
        pool = by_m.get(m, [])
        take = min(mn, len(pool))
        picks.extend(pool[:take])
        by_m[m] = pool[take:]

    if not fill_to_max:
        return picks

    # 2) top up toward max
    for m in muscles:
        mn, mx = quotas.get(m, quotas["_default"])
        pool = by_m.get(m, [])
        remaining = max(0, mx - sum(1 for ex in picks if ex["muscle"] == m))
        if remaining > 0 and pool:
            picks.extend(pool[:remaining])

    return picks

def _muscles_for_split(split):
    return MUSCLES_FOR_BLOCK.get(split) or COMBO_GROUPS.get(split, [])


class WorkoutPlanner:
    def __init__(self, source, **overrides):
        parsed = dict(source) if isinstance(source, dict) else ParseInput(source).parse()
        for k, v in (overrides or {}).items():
            if v not in (None, "", []):
                parsed[k] = v

        days_raw = parsed.get("num_days") or parsed.get("days") or 3
        try:
            days = int(days_raw)
        except:
            days = 3
        parsed["days"] = max(1, min(days, 7))

        diff = (parsed.get("difficulty") or "beginner").strip().lower()
        if diff == "advanced": diff = "expert"
        parsed["difficulty"] = diff
        parsed["equipment"] = parsed.get("equipment") or ["barbell", "dumbbell", "bodyweight", "cable"]
        self.parsed = parsed

    def _resolve_week_split(self):
        days = self.parsed["days"]
        diff = self.parsed["difficulty"]
        explicit = self.parsed.get("explicit_splits") or []

        if explicit:
            week = list(explicit)
        else:
            default = DEFAULT_SPLITS.get(days)
            if isinstance(default, list):
                week = default
            elif isinstance(default, dict):
                week = default.get(diff) or next(iter(default.values()))
            else:
                week = DEFAULT_SPLITS[3]["beginner"]

        if len(week) < 7:
            week = week + ["rest"] * (7 - len(week))
        return week[:7]

    def _fetch_for_split(self, split, equipment, difficulty):
        if split == "rest":
            return []

        muscles = _muscles_for_split(split)
        if not muscles:
            return []

        if split in BLOCK_SPLITS:
            candidates = fetch_by_block(split, equipment, difficulty, DB_PATH) or []
        else:
            candidates = fetch_by_muscles_quota(
                muscles=muscles,
                equipment=equipment,
                difficulty=difficulty,
                db_path=DB_PATH,
                quotas=MUSCLE_QUOTAS,
                shuffle=True,
            ) or []

        return _enforce_quotas(candidates, muscles, MUSCLE_QUOTAS, fill_to_max=True)


    def plan_workout(self):
        print("DEBUG parsed:", self.parsed)

        week = self._resolve_week_split()
        equip = self.parsed["equipment"]
        diff = self.parsed["difficulty"]

        plan = []
        for day, split in enumerate(week, 1):
            exs = self._fetch_for_split(split, equip, diff)
            plan.append({"day": day, "split": split, "exercises": exs})
        return plan

