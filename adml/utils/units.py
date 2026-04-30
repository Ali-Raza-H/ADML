PT_PER_PX = 0.75
PT_PER_MM = 2.83465
PT_PER_IN = 72.0
EMU_PER_PT = 12700

def to_points(value: float, unit: str) -> float:
    unit = unit.lower()
    if unit == "px":
        return value * PT_PER_PX
    if unit == "mm":
        return value * PT_PER_MM
    if unit == "in":
        return value * PT_PER_IN
    if unit == "pt":
        return value
    return value * PT_PER_PX  # default

def to_emu(value_pt: float) -> int:
    return int(value_pt * EMU_PER_PT)

def to_px(value_pt: float) -> float:
    return value_pt / PT_PER_PX

def to_mm(value_pt: float) -> float:
    return value_pt / PT_PER_MM

def parse_dimension(value: str) -> tuple[float, str]:
    import re
    match = re.match(r"(-?[0-9]+(?:\.[0-9]+)?)(px|pt|mm|in)?", value)
    if not match:
        try:
            return float(value), "px"
        except ValueError:
            return 0.0, "px"
    num, unit = match.groups()
    return float(num), unit or "px"
