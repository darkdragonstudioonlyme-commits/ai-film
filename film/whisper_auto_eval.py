from __future__ import annotations
import re
import unicodedata
from typing import Any

from .auto_eval import AutoEvalError

LANG_MAP = {"en": "en", "vi": "vi", "zh-CN": "zh", "zh": "zh"}

_ZH_VARIANT_MAP = str.maketrans({
    "為":"为","個":"个","還":"还","點":"点","車":"车","這":"这","裡":"里","裏":"里",
    "來":"来","復":"复","號":"号","臺":"台","門":"门","開":"开","關":"关","後":"后",
    "時":"时","間":"间","說":"说","話":"话","聽":"听","見":"见","從":"从","與":"与",
    "麼":"么","嗎":"吗","長":"长","頭":"头","發":"发","應":"应","讓":"让","樣":"样","諾":"诺",
})
_ZH_DIGITS = {"零":0,"〇":0,"一":1,"二":2,"两":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9}

def _parse_zh_under_100(token: str) -> int | None:
    if not token:
        return None
    if token.isdigit():
        return int(token)
    if token=="十":
        return 10
    if "十" in token:
        left,right=token.split("十",1)
        tens=1 if left=="" else _ZH_DIGITS.get(left)
        ones=0 if right=="" else _ZH_DIGITS.get(right)
        if tens is None or ones is None:
            return None
        return tens*10+ones
    if len(token)==1 and token in _ZH_DIGITS:
        return _ZH_DIGITS[token]
    return None

def _canonicalize_zh_time(text: str) -> str:
    text=text.translate(_ZH_VARIANT_MAP)
    pat=re.compile(r"([零〇一二两三四五六七八九十\d]{1,4})点([零〇一二两三四五六七八九十\d]{1,4})")
    def repl(m):
        hour=_parse_zh_under_100(m.group(1))
        minute=_parse_zh_under_100(m.group(2))
        if hour is None or minute is None:
            return m.group(0)
        return f"{hour}点{minute:02d}"
    return pat.sub(repl,text)

_VI_UNITS={"không":0,"một":1,"mot":1,"hai":2,"ba":3,"bốn":4,"bon":4,"tư":4,"tu":4,
           "năm":5,"nam":5,"lăm":5,"lam":5,"sáu":6,"sau":6,"bảy":7,"bay":7,
           "tám":8,"tam":8,"chín":9,"chin":9}

def _parse_vi_under_100(words: str) -> int | None:
    toks=words.strip().split()
    if not toks:
        return None
    if len(toks)==1:
        if toks[0].isdigit():
            return int(toks[0])
        if toks[0]=="mười":
            return 10
        return _VI_UNITS.get(toks[0])
    if toks[0]=="mười" and len(toks)==2:
        unit=_VI_UNITS.get(toks[1])
        return None if unit is None else 10+unit
    if len(toks) in {2,3} and toks[1] in {"mươi","muoi"}:
        tens=_VI_UNITS.get(toks[0])
        if tens is None:
            return None
        if len(toks)==2:
            return tens*10
        unit=_VI_UNITS.get(toks[2])
        if unit is None:
            return None
        if toks[2] in {"lăm","lam"}:
            unit=5
        elif toks[2] in {"mốt","mot"}:
            unit=1
        return tens*10+unit
    return None

def _canonicalize_vi_time(text: str) -> str:
    # Normalize numeric clock spellings such as 11h40/11 h 40.
    text=re.sub(r"\b(\d{1,2})\s*h\s*(\d{1,2})\b",lambda m:f"{int(m.group(1))}h{int(m.group(2)):02d}",text)
    number_words=r"(?:không|một|mot|hai|ba|bốn|bon|tư|tu|năm|nam|lăm|lam|sáu|sau|bảy|bay|tám|tam|chín|chin|mười|mươi|muoi|mốt)(?:\s+(?:không|một|mot|hai|ba|bốn|bon|tư|tu|năm|nam|lăm|lam|sáu|sau|bảy|bay|tám|tam|chín|chin|mười|mươi|muoi|mốt)){0,2}"
    pat=re.compile(rf"\b({number_words})\s+giờ\s+({number_words})\b")
    def repl(m):
        hour=_parse_vi_under_100(m.group(1))
        minute=_parse_vi_under_100(m.group(2))
        if hour is None or minute is None:
            return m.group(0)
        return f"{hour}h{minute:02d}"
    return pat.sub(repl,text)

def _norm(text: str, language: str | None=None) -> str:
    text = unicodedata.normalize("NFKC", text).casefold()
    lang=LANG_MAP.get(language or "",language or "")
    if lang=="zh":
        text=_canonicalize_zh_time(text)
        text=text.translate(_ZH_VARIANT_MAP)
    elif lang=="vi":
        text=_canonicalize_vi_time(text)
    text = re.sub(r"[^\w\s\u3400-\u9fff]", " ", text, flags=re.UNICODE)
    return " ".join(text.split())

def _lev(a: list[str], b: list[str]) -> int:
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(cur[-1] + 1, prev[j] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]

def text_match_score(target: str, transcript: str, language: str) -> float:
    target_n = _norm(target,language)
    transcript_n = _norm(transcript,language)
    if not target_n:
        raise AutoEvalError("Whisper target text empty")
    if LANG_MAP.get(language, language) == "zh":
        a = [c for c in target_n if not c.isspace()]
        b = [c for c in transcript_n if not c.isspace()]
    else:
        a = target_n.split()
        b = transcript_n.split()
    dist = _lev(a, b)
    return round(max(0.0, 1.0 - dist / max(1, len(a))) * 100.0, 6)

def build_whisper_receipt(
    *,
    asset_id: str,
    target_text: str,
    expected_language: str,
    transcript: str,
    detected_language: str,
    detected_probabilities: dict[str, float],
    model_sha256: str,
) -> dict[str, Any]:
    expected = LANG_MAP.get(expected_language, expected_language)
    match = text_match_score(target_text, transcript, expected_language)
    probs = {str(k): float(v) for k, v in detected_probabilities.items()}
    expected_prob = max(0.0, min(1.0, float(probs.get(expected, 0.0))))
    language_match = round(expected_prob * 100.0, 6)
    tags = []
    if detected_language != expected and expected_prob < 0.20:
        tags.append("WRONG_LANGUAGE")
    if match < 35.0:
        tags.append("SEVERE_TEXT_MISMATCH")
    return {
        "schema_version": 1,
        "evaluator_id": "whisper-turbo-asr",
        "asset_id": asset_id,
        "status": "PASS_MODEL_EVAL",
        "metrics": {"asr_text_match": match, "language_match": language_match},
        "hard_fail_tags": tags,
        "evidence": {
            "target_text": target_text,
            "transcript": transcript,
            "expected_language": expected,
            "detected_language": detected_language,
            "detected_language_probability": round(expected_prob, 6),
            "model_name": "turbo",
            "model_sha256": model_sha256,
        },
        "production_acceptance": False,
    }
