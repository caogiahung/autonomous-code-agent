\# 🤖 Autonomous Code Agent



An autonomous coding agent that reads GitHub issues, analyzes the codebase, writes fixes, and opens pull requests — powered by Claude AI.



\## What It Does



\- 📥 Reads open GitHub issues automatically

\- 🔍 Analyzes relevant files in the repository

\- 🛠️ Generates and validates code fixes

\- 🔐 Checks for common security issues (hardcoded secrets, injection risks)

\- 📤 Opens a pull request with the proposed fix



\## Setup

git clone https://github.com/YOUR\_USERNAME/autonomous-code-agent

cd autonomous-code-agent

pip install -r requirements.txt

cp .env.example .env

python main.py



\## Environment Variables



| Variable              | Description                        |

| `ANTHROPIC\_API\_KEY` | Your Anthropic Claude API key      |

| `GITHUB\_TOKEN`       | GitHub personal access token       |

| `GITHUB\_REPO`        | Target repo (e.g. `username/repo`) |



\## Tech Stack



\- Python 3.11+

\- Anthropic Claude API

\- PyGithub

## Roadmap
- [ ] Auto-assign issues to agent
- [ ] Slack notification on PR created
- [ ] Support for multi-file patches
