# 🤖 AI Autonomous QA Engineer

An end-to-end **AI-powered test automation platform**: upload a plain-text requirement document, and the system analyzes it, designs test scenarios and test cases, generates runnable Selenium scripts against the *real* DOM of your application, executes them with pytest, **self-heals failing tests using their runtime errors**, and tracks pass-rate trends over time.

Built with FastAPI, Streamlit, Selenium, and Groq LLMs (Llama 3.3 70B).

## ✨ Key Features

- **4-stage LLM pipeline** — requirement analysis → test scenarios → detailed test cases → Selenium scripts, each stage validated against pydantic schemas with automatic JSON repair and retries.
- **Real-DOM grounding** — before generating code, a headless Chrome scans the target application (waiting for JavaScript rendering) and hands the AI the actual inputs, buttons, and locators, preventing hallucinated selectors.
- **Script quality gate** — every generated script is AST-parsed and validated: pytest structure enforced, fragile locators rejected, placeholder credentials rejected, hallucinated features rejected. Invalid scripts are skipped with logged reasons, never executed blindly.
- **🩹 Self-healing tests** — when a test fails at runtime, one click sends the failing script plus its actual pytest traceback back to the LLM, applies the corrected script, and re-runs the suite.
- **Execution history & trends** — every run is persisted with pass/fail counts and duration; the dashboard shows pass-rate and duration trends across runs.
- **One-click pipeline UI** — Streamlit frontend with step-by-step pages or a single "Run Full Pipeline" button, embedded HTML reports, and a download center.
- **Security hardening** — path-traversal-safe uploads (UUID-prefixed, extension whitelist), sanitized AI-chosen filenames, secrets kept out of git.
- **CI-tested** — unit tests for the sanitizer, script validator, schemas, and output parsers run on every push via GitHub Actions, plus Docker build verification.

## 🏗 Architecture

```
┌─────────────┐     ┌──────────────────────────────────────────┐
│  Streamlit  │     │              FastAPI backend             │
│  frontend   │────▶│                                          │
│  (8501)     │     │  /upload             requirement docs    │
└─────────────┘     │  /generate-scenarios LLM + schema check  │
                    │  /generate-testcases LLM + schema check  │
                    │  /generate-selenium  DOM scan + LLM +    │
                    │                      quality gate        │
                    │  /execute            pytest + Chrome     │
                    │  /heal               AI self-healing     │
                    └───────────┬──────────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │ headless Chrome       │──▶ target web app
                    │ (DOM scan + tests)    │
                    └───────────────────────┘
```

**Pipeline flow:** `requirement.txt` → RequirementAnalyzer → TestScenarioGenerator → TestCaseGenerator → DOM scan → SeleniumGenerator → quality gate → pytest execution → HTML report + history → (on failure) self-healing loop.

## 🚀 Quick Start (Docker)

```bash
git clone https://github.com/<your-username>/ai-autonomous-qa.git
cd ai-autonomous-qa

cp .env.example .env        # add your GROQ_API_KEY (free at console.groq.com)

docker compose up --build
```

Open **http://localhost:8501**, upload a requirement document (see `sample_requirement.txt`), enter the application URL, and press **Run Full Pipeline**.

API docs: http://localhost:8000/docs

### Try it against the OrangeHRM demo

Application URL: `https://opensource-demo.orangehrmlive.com/`

Add to `.env` so the login tests can authenticate:

```
TEST_USERNAME=Admin
TEST_PASSWORD=admin123
```

## 🖥 Local Development (without Docker)

```bash
python -m venv venv
venv\Scripts\activate            # Windows  (source venv/bin/activate on Linux/Mac)
pip install -r requirements.txt
cp .env.example .env             # add your key

# terminal 1 — backend
uvicorn app.main:app --reload

# terminal 2 — frontend
streamlit run frontend/app.py
```

Requires Google Chrome installed locally (Selenium Manager fetches the driver automatically).

## 🧪 Running the Unit Tests

```bash
pytest tests/ -v
```

Covers the upload sanitizer (path-traversal defense), the Selenium script quality gate, the pydantic schemas, and the pytest output parsers. The same suite runs in CI on every push.

## 📁 Project Structure

```
app/
  agents/          LLM agents (analysis, scenarios, test cases, selenium, DOM)
  api/             FastAPI routers (upload, scenarios, testcases, selenium, execute/heal)
  core/            AI client (lazy singleton), settings, prompt loader
  prompts/         LLM prompt templates
  readers/         PDF / DOCX / TXT extraction
  schemas/         pydantic models for every pipeline stage
  services/        DOM scan, execution, self-healing, history
frontend/
  app.py           dashboard (backend health, pipeline progress)
  pages/           one-click pipeline + step-by-step pages + reports/history
tests/             unit tests (run in CI)
.github/workflows/ CI: unit tests + Docker build
```

## ⚠️ Notes & Limitations

- Generated tests target the **landing page** of the URL you provide; features hidden behind deep navigation get weaker coverage (multi-page crawling is on the roadmap).
- Sites with CAPTCHAs or bot protection cannot be tested headlessly.
- A failing generated test on a real site is often *correct behavior* — read the HTML report before assuming a bug.
- The `/execute` endpoint runs generated code; deploy behind authentication if exposed beyond localhost.

## 🗺 Roadmap

Multi-page DOM crawling · test case export to Excel/Jira · parallel execution (pytest-xdist) · run comparison view · pluggable LLM providers.

## 📄 License

MIT — see [LICENSE](LICENSE).
