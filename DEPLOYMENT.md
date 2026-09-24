# GitHub + Streamlit Deployment

## 1. Unzip the project on your Mac

Double-click the ZIP file.

Open the resulting folder. You should see:

- `app.py`
- `simulation.py`
- `README.md`
- `DEPLOYMENT.md`
- `requirements.txt`

You should also have:

- `.gitignore`
- `.streamlit/config.toml`

On macOS, press `Command + Shift + .` in Finder if hidden dot-files are not visible.

## 2. Create the GitHub repository

Recommended repository name:

`flowloop-process-control`

Recommended description:

`Interactive PI process-control demo for pipeline flow setpoint tracking, disturbance rejection, and controller saturation.`

Make it public if you want recruiters to be able to open it.

Do not initialize the repo with another README or .gitignore.

## 3. Upload files

Use GitHub:

`Add file -> Upload files`

Drag the **contents of the unzipped folder** into GitHub.

The repository root should look like:

```text
app.py
simulation.py
README.md
DEPLOYMENT.md
requirements.txt
.gitignore
.streamlit/
```

Commit with:

`Initial FlowLoop process-control demo`

## 4. Deploy to Streamlit

Open Streamlit Community Cloud and create a new app.

Use:

- Repository: `YOUR_USERNAME/flowloop-process-control`
- Branch: `main`
- Main file path: `app.py`

Suggested custom URL:

`kshipra-flowloop`

No secrets are required.

## 5. Test the deployed app

Run these three cases:

1. Balanced + No disturbance
2. Balanced + Mild restriction
3. Balanced + Severe restriction

The severe restriction should drive the controller toward 100% output while actual
flow remains below a 1000 bbl/h setpoint.
