from transformers import pipeline
import torch
import re


WORD2NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7}
DIFFICULTY_LABELS = ['beginner', 'intermediate', 'expert']
SPLIT_LABELS = ['push', 'pull', 'leg', 'upper', 'lower', 'full', 'chest', 'arm', 'bicep', 'tricep', 'shoulder', 'back', 'abs']
ROTATION = ['push', 'pull', 'legs']
EQUIPMENTS = ['bodyweight', 'cable', 'machine', 'sled', 'ropes', 'barbell', 'dumbbell', 'kettlebell', 'bands']
DEFAULT_EQUP = ["barbell","dumbbell","bodyweight","cable"]
MUSCLE_LABELS = ['abdominals', 'abductors', 'adductors', 'biceps', 'calves', 'chest', 'forearms', 'glutes',
'hamstrings', 'lats', 'lower back', 'middle back', 'neck', 'quadriceps', 'traps', 'triceps', 'shoulders']
SPECDAYS = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
NEG_CUES = r"\b(can't|cannot|won't|no|except|but\s+not|not\s+on)\b"
_CANON = {
    'leg': 'legs', 'legs': 'legs',
    'arm': 'arms', 'arms': 'arms',
    'bicep': 'biceps', 'biceps': 'biceps',
    'tricep': 'triceps', 'triceps': 'triceps',
    'shoulder': 'shoulders', 'shoulders': ['front delts', 'side delts', 'rear delts'],
    'abdominal': 'abs', 'abdominals': 'abs', 'abs': 'abs'
}

class ParseInput:
    def __init__(self, text):
        self.pipe = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-1", device=0)
        self.text = text.strip().lower()

    def extract_days(self):
        t = self.text
        m = re.search(r"\b(one|two|three|four|five|six|seven|\d+)\s*-?\s*days?\b", t)
        if not m:
            return 1
        tok = m.group(1)
        return max(1, min(int(tok) if tok.isdigit() else WORD2NUM[tok], 7))


    def classify_split(self, num_days=None):
        def _extract_explicit_splits(t: str):
            day_hits = re.findall(
                r"\b(push|pull|legs?|upper|lower|full|chest|back|shoulders?|arms?|biceps?|triceps?|abs)\s*(?:day|workout)?\b",
                t
            )

            list_hits = []
            for chunk in re.split(r"[.;\n]", t):
                if "/" in chunk or "," in chunk:
                    parts = re.split(r"[\/,]\s*", chunk)
                    for p in parts:
                        m = re.match(
                            r"\b(push|pull|legs?|upper|lower|full|chest|back|shoulders?|arms?|biceps?|triceps?|abs)\b",
                            p.strip()
                        )
                        if m:
                            list_hits.append(m.group(1))

            hits = day_hits + list_hits
            return [_CANON.get(h, h) for h in hits] if hits else []

        if num_days is None:
            num_days = self.extract_days()

        explicit = _extract_explicit_splits(self.text)
        if explicit:
            return [explicit[i % len(explicit)] for i in range(num_days)]

        return []


    def classify_difficulty(self):
        d = self.text
        dif = self.pipe(d, candidate_labels=DIFFICULTY_LABELS)
        top_label = dif["labels"][0]
        return top_label

    def extract_equipment(self, threshold=0.3):
        e = self.text
        equip = self.pipe(e, candidate_labels=EQUIPMENTS)
        if not equip or "labels" not in equip:
            return DEFAULT_EQUP

        chosen = [label for label, score in zip(equip["labels"], equip["scores"]) if score >= threshold]
        return chosen or DEFAULT_EQUP

    def specific_days(self, threshold=0.3):
        sd = self.text

        hits = set()

        if hits:
            is_negative = re.search(NEG_CUES, sd) is not None
            if is_negative:
                unavailable = sorted(hits)
                available = [d for d in SPECDAYS if d not in unavailable]
                return {"available": available, "unavailable": unavailable}
            else:
                return {"available": sorted(hits), "unavailable": []}

        spec_day = self.pipe(sd, candidate_labels=SPECDAYS, multi_label=True)
        chosen = [label for label, score in zip(spec_day["labels"], spec_day["scores"]) if score >= threshold]
        if not chosen:
            return {"available": SPECDAYS[:], "unavailable": []}
        return {"available": chosen, "unavailable": []}

    def parse(self):
        t = self.text

        if not t:
            return {"difficulty": "beginner", "days": 3, "explicit_splits": []}

        final = {
            "num_days": self.extract_days(),
            "difficulty": self.classify_difficulty(),
            "explicit_splits": self.classify_split() or [],
            "specific_days": self.specific_days(),
            "equipment": self.extract_equipment() or [],
            "user_text": self.text,
                 }
        return final

