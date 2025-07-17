# 📬 Smart Job Alerts

**Automatically find and send job alerts tailored to your resume and job preferences.**
This app fetches job postings using JSearch, a powerful job listing API available on RapidAPI. For each job, it uses your resume and a customizable LLM prompt to evaluate relevance via OpenRouter (supporting models like Moonshot or DeepSeek). It compares jobs against a user-defined match threshold and sends an email containing the top matches — each with a match score and a short summary explaining why the job does or doesn’t match.
**You can run the app automatically using GitHub Actions to receive alerts on a regular schedule (e.g., once a day).**


<p align="center">
  <img src="./assets/smart_job_alerts.png" alt="Job Matching Flowchart" width="600"/>
</p>

---

## 📑 Table of Contents

- [🎯 Goal](#-goal)
- [🚀 Two Ways to Use This App](#-two-ways-to-use-this-app)
- [🧠 How It Works](#-how-it-works)
- [📦 Required Files & Configurations](#-required-files--configurations)
- [📩 Step 1: Set Up API Access](#-step-1-set-up-api-access)
- [⚙️ Option 1: GitHub Action Setup (Automatic Email Alerts)](#️-option-1-github-action-setup-automatic-email-alerts)
- [🐳 Option 2: Run with Docker Locally (Manual Email Alerts)](#-option-2-run-with-docker-locally-manual-email-alerts)
- [🛠 Example Prompt Template](#-example-prompt-template)
- [🧪 Testing Locally](#-testing-locally)
- [✉️ Example Alert Email](#️-example-alert-email)
- [📜 License](#-license)
- [🙋 Questions?](#-questions)

---

## 🎯 Goal

Manually searching job boards is time-consuming. Smart Job Alerts automates this by:

- Fetching fresh job listings from the **JSearch API (via RapidAPI)**
- Using your **resume** and a **prompt template** to assess relevance using **LLMs** (e.g., Moonshot/Kimi-K2 via OpenRouter)
- Emailing you the top job matches with detailed feedback

---

## 🚀 Two Ways to Use This App

### Option 1: Use GitHub Actions (Automatic Alerts)

Automatically run the job matching every day (or on schedule) using GitHub Actions.

### Option 2: Use Docker Locally (Manual Alerts)

Run the app manually using a Docker image. Recommended if you prefer CLI over GitHub automation.

---

## 🧠 How It Works

1. You provide a **resume (PDF)** and a **prompt template**.
2. Jobs are fetched from RapidAPI.
3. For each job, the full job description + qualifications/responsibilities are passed to an LLM.
4. The LLM scores each job and provides a justification.
5. Matching jobs are emailed to you using Gmail SMTP.

---

## 📦 Required Files & Configurations

These files must exist before running the app:

| File                          | Description                                                                 |
| ----------------------------- | --------------------------------------------------------------------------- |
| `.env`                        | API keys and email credentials (based on `.env.example`)                    |
| `data/resume.pdf`             | Your actual resume (PDF format)                                             |
| `data/prompt_template.txt`    | LLM prompt template with placeholders like `{resume_text}` and `{job_desc}` |
| `data/seen_jobs.json`         | Tracks which jobs you've already seen (starts as empty `[]`)                |
| `data/blocked_employers.yaml` | Employers you want to skip (starts as `blocked_employers: []`)              |
| `config.yaml`                 | Job search filters (keywords, location, email, thresholds, etc.)            |

---

## 📩 Step 1: Set Up API Access

You need a **RapidAPI account** to fetch job data.

1. Sign up at [rapidapi.com](https://rapidapi.com/)
2. Subscribe to the **JSearch API** (free tier available)
3. Note your:
   - `RAPIDAPI_KEY`
   - `RAPIDAPI_HOST` (usually `jsearch.p.rapidapi.com`)

You also need:

- A Gmail account with **App Password** enabled (for sending alerts)
- An account on [OpenRouter.ai](https://openrouter.ai) to get an API key for LLM access

---

## ⚙️ Option 1: GitHub Action Setup (Automatic Email Alerts)

### 🧬 Prerequisites

- GitHub account
- Resume PDF & config files prepared

### 🛠️ Step-by-Step:

1. **Clone the Repo**

   ```bash
   git clone https://github.com/msmalmir/Smart-Job-Alerts.git
   cd Smart-Job-Alerts


Ready to automate your job hunt? 🚀


