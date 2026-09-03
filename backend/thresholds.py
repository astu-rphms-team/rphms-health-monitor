"""
Configurable thresholds for vital sign status classification.

IMPORTANT (state this in your report / defense):
This system is for HEALTH MONITORING AND ALERTING ONLY.
It is NOT a medical diagnostic device and must not be used to make
clinical decisions. Always consult a qualified healthcare professional.

Adjust the numbers below to change what counts as normal / warning / critical.
"""

# Heart rate (beats per minute)
HR_NORMAL_MIN, HR_NORMAL_MAX = 60, 100
HR_WARNING_MIN, HR_WARNING_MAX = 50, 120
# below HR_WARNING_MIN or above HR_WARNING_MAX = critical

# SpO2 (blood oxygen saturation, %)
SPO2_NORMAL_MIN = 95
SPO2_WARNING_MIN = 90
# below SPO2_WARNING_MIN = critical

# Body temperature (Celsius)
TEMP_NORMAL_MIN, TEMP_NORMAL_MAX = 36.1, 37.5
TEMP_WARNING_MIN, TEMP_WARNING_MAX = 35.5, 38.5
# below TEMP_WARNING_MIN or above TEMP_WARNING_MAX = critical


def classify_heart_rate(hr: float) -> str:
    if hr is None:
        return "normal"
    if HR_NORMAL_MIN <= hr <= HR_NORMAL_MAX:
        return "normal"
    if HR_WARNING_MIN <= hr <= HR_WARNING_MAX:
        return "warning"
    return "critical"


def classify_spo2(spo2: float) -> str:
    if spo2 is None:
        return "normal"
    if spo2 >= SPO2_NORMAL_MIN:
        return "normal"
    if spo2 >= SPO2_WARNING_MIN:
        return "warning"
    return "critical"


def classify_temperature(temp: float) -> str:
    if temp is None:
        return "normal"
    if TEMP_NORMAL_MIN <= temp <= TEMP_NORMAL_MAX:
        return "normal"
    if TEMP_WARNING_MIN <= temp <= TEMP_WARNING_MAX:
        return "warning"
    return "critical"


# Overall status = the worst of the three individual statuses
_SEVERITY_ORDER = {"normal": 0, "warning": 1, "critical": 2}


def overall_status(hr: float, spo2: float, temp: float) -> str:
    statuses = [
        classify_heart_rate(hr),
        classify_spo2(spo2),
        classify_temperature(temp),
    ]
    worst = max(statuses, key=lambda s: _SEVERITY_ORDER[s])
    return worst
