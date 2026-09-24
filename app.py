import pandas as pd
import streamlit as st

from simulation import performance_metrics, simulate_flow_loop


st.set_page_config(
    page_title="FlowLoop | PI Pipeline Flow Control Demo",
    page_icon="〰️",
    layout="wide",
)

st.title("FlowLoop")
st.markdown("**A PI controller for maintaining pipeline flow under disturbances**")
st.caption("Developed by Kshipra S. Kapoor, PhD")

st.info(
    "Think of this like cruise control for a pipeline. You choose the desired flow rate, "
    "and the controller automatically adjusts its output to keep the flow near that target. "
    "Then you can introduce a downstream restriction and watch how the controller responds — "
    "including what happens when the physical process can no longer achieve the requested flow."
)

tab_sim, tab_explain = st.tabs(["Run Simulation", "How It Works"])

with tab_sim:
    st.subheader("1. Choose the controller settings")

    preset = st.selectbox(
        "Controller tuning",
        ["Balanced", "Gentle", "Fast", "Custom"],
    )

    presets = {
        "Gentle": (0.50, 0.012),
        "Balanced": (1.00, 0.040),
        "Fast": (1.40, 0.070),
    }

    if preset == "Custom":
        c1, c2 = st.columns(2)
        kp = c1.slider("Kp — proportional gain", 0.0, 3.0, 1.0, 0.05)
        ki = c2.slider("Ki — integral gain", 0.0, 0.15, 0.04, 0.005)
    else:
        kp, ki = presets[preset]
        c1, c2 = st.columns(2)
        c1.metric("Kp", f"{kp:.3f}")
        c2.metric("Ki", f"{ki:.3f}")

    c1, c2 = st.columns(2)

    setpoint = c1.slider(
        "Desired flow setpoint (bbl/h)",
        min_value=700,
        max_value=1100,
        value=1000,
        step=25,
    )

    disturbance = c2.selectbox(
        "Process condition at t = 150 s",
        ["No disturbance", "Mild restriction", "Severe restriction"],
    )

    st.caption(
        "The downstream restriction is modeled by reducing how much flow the process "
        "can produce for a given controller output."
    )

    df = simulate_flow_loop(
        setpoint=float(setpoint),
        kp=float(kp),
        ki=float(ki),
        disturbance=disturbance,
    )
    metrics = performance_metrics(
        df,
        setpoint=float(setpoint),
        disturbance=disturbance,
    )

    st.divider()
    st.subheader("2. Watch the loop respond")

    flow_plot = df.set_index("Time (s)")[
        ["Flow (bbl/h)", "Setpoint (bbl/h)"]
    ]
    st.markdown("#### Flow response")
    st.line_chart(flow_plot)

    st.markdown("#### Controller output")
    st.line_chart(
        df.set_index("Time (s)")[["Controller Output (%)"]]
    )

    st.markdown("#### Process capability")
    st.line_chart(
        df.set_index("Time (s)")[
            ["Process Gain (bbl/h at 100%)"]
        ]
    )

    st.divider()
    st.subheader("3. Basic performance metrics")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "Initial overshoot",
        f"{metrics['Overshoot (%)']:.1f}%",
    )

    initial_settle = metrics["Initial settling time (s)"]
    m2.metric(
        "Initial settling time",
        "Not settled" if initial_settle is None else f"{initial_settle:.0f} s",
    )

    m3.metric(
        "Final flow error",
        f"{metrics['Final flow error (%)']:.1f}%",
    )

    m4.metric(
        "Controller saturation",
        f"{metrics['Time saturated after disturbance (s)']:.0f} s",
    )

    st.markdown("#### What should I notice?")

    if disturbance == "No disturbance":
        st.write(
            "The PI controller adjusts its output until actual flow approaches the setpoint. "
            "Try changing the tuning preset to see how response speed and overshoot change."
        )

    elif disturbance == "Mild restriction":
        st.write(
            "At 150 s the same controller output produces less flow. The PI controller reacts "
            "by increasing its output and can usually recover the requested flow."
        )

    else:
        st.warning(
            "The severe restriction reduces the process capability below the requested setpoint. "
            "The controller reaches 100% output but cannot restore the requested flow. "
            "This is a process limitation, not simply a controller-tuning problem."
        )

    st.markdown("#### Final operating point")
    final = df.iloc[-1]

    final_table = pd.DataFrame(
        {
            "Variable": [
                "Requested flow",
                "Actual flow",
                "Controller output",
                "Flow error",
            ],
            "Value": [
                f"{setpoint:.0f} bbl/h",
                f"{final['Flow (bbl/h)']:.1f} bbl/h",
                f"{final['Controller Output (%)']:.1f}%",
                f"{final['Error (bbl/h)']:.1f} bbl/h",
            ],
        }
    )

    st.dataframe(
        final_table,
        hide_index=True,
        use_container_width=True,
    )


with tab_explain:
    st.subheader("The whole project in two equations")

    st.markdown("### 1. Simplified pipeline-flow process")
    st.latex(r"\tau \frac{dQ}{dt} + Q = K u")

    st.markdown(
        """
- **Q** = flow rate
- **u** = controller output from 0 to 100%
- **K** = process gain / approximate flow capability
- **τ** = process time constant

Increasing the controller output increases flow, but the process does not respond instantly.
"""
    )

    st.markdown("### 2. PI controller")

    st.latex(r"u(t)=K_p e(t)+K_i\int e(t)\,dt")
    st.latex(r"e(t)=Q_{SP}-Q(t)")

    st.markdown(
        """
The proportional term reacts to the current error. The integral term accumulates
error over time so the controller can remove persistent offset.
"""
    )

    st.markdown("### What does the disturbance mean?")

    st.markdown(
        """
At **150 seconds**, the simulator can reduce the process gain:

- **No disturbance:** normal process conditions
- **Mild restriction:** flow capability decreases, but the controller can still recover
- **Severe restriction:** flow capability drops below the requested flow

In the severe case, the controller reaches its maximum output but still cannot
restore the requested flow.
"""
    )

    st.markdown("### What this demo shows")

    st.write(
        "A controller can automatically compensate for moderate changes in the process. "
        "But if a restriction becomes severe enough, the controller may reach its maximum "
        "output and still be unable to maintain the requested flow. This illustrates an "
        "important troubleshooting principle: sometimes the controller is working correctly, "
        "but the physical process has become the limiting factor."
    )

    st.markdown("### Try it yourself")

    st.write(
        "Compare the No Disturbance, Mild Restriction, and Severe Restriction cases. "
        "Watch how the actual flow and controller output change, and experiment with the "
        "controller tuning to see how different settings affect the system response."
    )

    st.caption(
        "This demonstration uses a simplified synthetic process model for learning and visualization."
    )
