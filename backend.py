import numpy as np
from mc_simulation import MC

# ── Sensor definitions ────────────────────────────────────────────
SENSORS = {
    'MEMS': {'b': 3,    'ARW': 0.15,    'BI': 0.5,  'tau': 600},
    'IFOG': {'b': 0.1,  'ARW': 0.03126, 'BI': 1,    'tau': 3000},
    'RLG':  {'b': 1,    'ARW': 0.02,    'BI': 0.1,  'tau': 5000},
}

MC_RUNS = 500
DT_SEC  = 0.1
THETA_POINTING = 0.1

# Fixed error budget components (deg)
THETA_GIMBAL    = 0.05
THETA_STRUCTURE = 0.04
THETA_TRACKING  = 0.03


def run_analysis(f_hz: float, D: float, T_sec: float) -> dict:
    """
    Run the full antenna / INS analysis.

    Parameters
    ----------
    f_hz  : frequency in Hz  (e.g. 14e9 for 14 GHz)
    D     : antenna diameter in metres
    T_sec : mission duration in seconds

    Returns
    -------
    dict with keys:
        beamwidth, theta_INS_allow,
        results   -> {name: {'rms': float, 'pass': bool}},
        passing   -> [name, ...],
        T_sec, f_hz, D,
        error     -> str | None
    """
    c = 3e8
    lambda_val = c / f_hz
    theta_BW   = (70 * lambda_val) / D

    # Error budget
    remaining = (THETA_POINTING**2
                 - THETA_GIMBAL**2
                 - THETA_STRUCTURE**2
                 - THETA_TRACKING**2)

    if remaining <= 0:
        return {'error': 'Error budget exceeded before INS allocation.'}

    theta_INS_allow = np.sqrt(remaining)

    # MC parameters
    T_hr  = T_sec / 3600
    dt_hr = DT_SEC / 3600
    N     = int(T_sec / DT_SEC)

    results = {}
    for name, sensor in SENSORS.items():
        rms  = MC(sensor, T_hr, DT_SEC, dt_hr, N, MC_RUNS)
        results[name] = {'rms': rms, 'pass': bool(rms <= theta_INS_allow)}

    passing = [n for n, v in results.items() if v['pass']]

    return {
        'error':           None,
        'f_hz':            f_hz,
        'D':               D,
        'T_sec':           T_sec,
        'beamwidth':       theta_BW,
        'theta_INS_allow': theta_INS_allow,
        'results':         results,
        'passing':         passing,
    }
