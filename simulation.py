import numpy as np
import pandas as pd


def simulate_flow_loop(
    setpoint=1000.0,
    kp=1.0,
    ki=0.04,
    disturbance="Mild restriction",
    disturbance_time=150,
    total_time=300,
    dt=1.0,
    initial_flow=700.0,
    process_gain_normal=1200.0,
    process_time_constant=35.0,
):
    """
    Simple educational PI flow-control simulation.

    Process model:
        tau * dQ/dt + Q = K * u

    where:
        Q = pipeline flow (bbl/h)
        u = controller output, 0 to 1
        K = process gain / approximate maximum achievable flow
        tau = process time constant

    A downstream restriction is represented by reducing K after disturbance_time.
    """

    restriction_gains = {
        "No disturbance": process_gain_normal,
        "Mild restriction": 1050.0,
        "Severe restriction": 850.0,
    }

    restricted_gain = restriction_gains[disturbance]

    q = float(initial_flow)
    integral = 0.0
    rows = []

    for t in np.arange(0, total_time + dt, dt):
        process_gain = (
            process_gain_normal
            if t < disturbance_time or disturbance == "No disturbance"
            else restricted_gain
        )

        error = setpoint - q
        normalized_error = error / max(setpoint, 1.0)

        # Candidate integral update.
        integral_candidate = integral + normalized_error * dt

        # PI controller. Output is a fraction from 0 to 1.
        u_unclipped = kp * normalized_error + ki * integral_candidate
        u = float(np.clip(u_unclipped, 0.0, 1.0))

        # Simple anti-windup:
        # integrate when unsaturated, or when error would move the controller
        # back toward the valid output range.
        if (
            0.0 < u_unclipped < 1.0
            or (u_unclipped >= 1.0 and normalized_error < 0.0)
            or (u_unclipped <= 0.0 and normalized_error > 0.0)
        ):
            integral = integral_candidate

        # First-order process response.
        dq_dt = (process_gain * u - q) / process_time_constant
        q = q + dq_dt * dt

        rows.append(
            {
                "Time (s)": float(t),
                "Flow (bbl/h)": float(q),
                "Setpoint (bbl/h)": float(setpoint),
                "Controller Output (%)": float(u * 100.0),
                "Process Gain (bbl/h at 100%)": float(process_gain),
                "Error (bbl/h)": float(setpoint - q),
            }
        )

    return pd.DataFrame(rows)


def _settling_time(df, setpoint, start_time=0, tolerance_pct=2.0, hold_seconds=10):
    """
    First time after start_time that flow remains within the tolerance band
    for hold_seconds consecutive samples.
    """
    work = df[df["Time (s)"] >= start_time].reset_index(drop=True)
    if work.empty:
        return None

    tol = abs(setpoint) * tolerance_pct / 100.0
    inside = (work["Flow (bbl/h)"] - setpoint).abs() <= tol

    run = 0
    for i, ok in enumerate(inside):
        if ok:
            run += 1
            if run >= hold_seconds:
                idx = i - hold_seconds + 1
                return float(work.loc[idx, "Time (s)"] - start_time)
        else:
            run = 0
    return None


def performance_metrics(df, setpoint, disturbance, disturbance_time=150):
    """
    Small set of intuitive controller-performance metrics.
    """
    pre = df[df["Time (s)"] < disturbance_time]
    post = df[df["Time (s)"] >= disturbance_time]

    initial_peak = float(pre["Flow (bbl/h)"].max()) if not pre.empty else float(df["Flow (bbl/h)"].max())
    overshoot_pct = max(0.0, (initial_peak - setpoint) / max(setpoint, 1.0) * 100.0)

    final_flow = float(df["Flow (bbl/h)"].iloc[-1])
    final_error_pct = abs(setpoint - final_flow) / max(setpoint, 1.0) * 100.0

    saturated_seconds = float(
        (post["Controller Output (%)"] >= 99.9).sum()
    )

    initial_settling = _settling_time(df, setpoint, start_time=0)

    if disturbance == "No disturbance":
        recovery = None
    else:
        recovery = _settling_time(
            df,
            setpoint,
            start_time=disturbance_time,
        )

    return {
        "Overshoot (%)": overshoot_pct,
        "Final flow error (%)": final_error_pct,
        "Initial settling time (s)": initial_settling,
        "Recovery time after disturbance (s)": recovery,
        "Time saturated after disturbance (s)": saturated_seconds,
        "Final flow (bbl/h)": final_flow,
    }
