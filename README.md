# FlowLoop
### A simple PI controller for maintaining pipeline flow under disturbances

FlowLoop is a small Python/Streamlit process-control demo created to explore a basic
pipeline-control question:

> How does a PI controller maintain flow when the process changes?

The project is deliberately simple. It is **not** an AI application and it is not a
field-calibrated pipeline simulator.

## What it demonstrates

- first-order process dynamics;
- proportional-integral (PI) control;
- flow setpoint tracking;
- mild and severe downstream restrictions;
- controller saturation;
- overshoot and settling time;
- the difference between a controller problem and a process limitation.

## Process model

The synthetic process is:

```text
tau * dQ/dt + Q = K * u
```

where:

- `Q` = pipeline flow in bbl/h;
- `u` = controller output from 0 to 1;
- `K` = synthetic process gain / flow capability;
- `tau` = process time constant.

The controller is:

```text
u(t) = Kp * e(t) + Ki * integral(e(t))
e(t) = Q_setpoint - Q(t)
```

The output is constrained to 0–100%, and the code includes a simple anti-windup rule.

## Disturbance

At `t = 150 s`, the user may select:

- **No disturbance** — process gain remains 1200 bbl/h at 100% output.
- **Mild restriction** — process gain falls to 1050 bbl/h.
- **Severe restriction** — process gain falls to 850 bbl/h.

With a 1000 bbl/h setpoint, the mild case can still recover. In the severe case,
the process physically cannot achieve the requested flow, so the controller saturates.

That is the main troubleshooting lesson of the project.

## Files

```text
flowloop/
├── app.py
├── simulation.py
├── README.md
├── DEPLOYMENT.md
├── requirements.txt
├── .gitignore
└── .streamlit/
    └── config.toml
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

On Windows:

```text
.venv\Scripts\activate
```

## Deploy on Streamlit Community Cloud

Create a public GitHub repository such as:

```text
flowloop-process-control
```

Upload the project files so that `app.py` is at the repository root.

Then deploy with:

- Repository: your GitHub repository
- Branch: `main`
- Main file path: `app.py`

No secrets or API keys are required.

## Suggested GitHub description

> Interactive PI process-control demo for pipeline flow setpoint tracking, disturbance rejection, and controller saturation.

## Suggested interview explanation

> I built a small first-order pipeline-flow simulator because I wanted to understand
> the process-control problem directly. A PI controller maintains a flow setpoint,
> and I introduce a downstream restriction to see how the loop responds. In the mild
> case the controller compensates by increasing its output. In the severe case the
> controller saturates at 100%, but flow remains below setpoint, which shows that the
> underlying process—not just controller tuning—can be the limiting factor.

## Disclaimer

This project is an educational reduced-order simulation. It is not based on
ExxonMobil proprietary data or control logic and is not intended for operational use.
