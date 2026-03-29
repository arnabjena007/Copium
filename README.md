 CloudCFO 
> **Last updated:** 2026-03-28 01:10 IST

---

## 📋 Project Description

**CloudCFO** is an AWS cost-optimization automation platform that detects cost anomalies, identifies idle resources, and delivers actionable alerts via Slack — complete with interactive "Fix" buttons for one-click remediation.

### Core Goals
- **Detect** cost spikes and anomalies across AWS accounts in real time
- **Identify** idle/underutilized resources (EC2, EBS, etc.)
- **Alert** teams via Slack with rich Block Kit messages
- **Remediate** with one-click "Fix" buttons that trigger safe, audited actions
- **Report** daily cost summaries with forecasts and savings opportunities


| Date | Action | Details |
|---|---|---|
| 2026-03-27 | **Project init** | Created `requirements.txt`, `.gitignore`, `.env.example`, `config/settings.py` |
| 2026-03-27 | **Data models** | Built `models.py` with 5 Pydantic models: `CostAnomaly`, `IdleResource`, `RemediationAction`, `AlertPayload`, `AlertSeverity` |
| 2026-03-27 | **Webhook client** | Built `webhook.py` with retry logic, rate-limit handling, and URL validation |
| 2026-03-27 | **Message builder** | Built `message_builder.py` with 3 Block Kit message types |
| 2026-03-27 | **Alert service** | Built `alert_service.py` facade combining models + builder + webhook |
| 2026-03-27 | **Demo & tests** | Created `demo_slack.py` (5 demo modes) and `test_slack.py` (19 unit tests, all passing) |
| 2026-03-27 | **Venv + Git** | Created `.venv`, initialized git, connected to GitHub remote |
| 2026-03-27 | **First push** | Force-pushed Phase 1 to `main` branch on GitHub |
| 2026-03-27 | **Slack workspace** | Created "Cloudcfo" Slack workspace, `#new-channel`, and "webhooks" app |
| 2026-03-27 | **Live E2E test** | Sent 5 alerts to Slack — all delivered and formatted correctly |
| 2026-03-27 | **Cleanup** | Removed demo script and test files, pushed cleanup commit to GitHub |
| 2026-03-28 | **Phase 2 scaffold** | Added `RemediationEngine` with EC2 stop, EBS delete, EC2 rightsize, dry-run handling, and JSON audit logging |
| 2026-03-28 | **Phase 3 scaffold** | Added Cost Explorer anomaly detector, threshold settings, and daily scan runner for Slack alerts |
| 2026-03-28 | **Phase 2 complete** | Added `ConfirmationGate`, `start_ec2()`, `snapshot_and_delete_ebs()`, `list_actions()`, `PendingAction` lifecycle tracking |
| 2026-03-28 | **Phase 4 complete** | Built FastAPI server, hooked up Slack signature verification, mapped buttons to boto3 background execution, pushed final results back to Slack. |
| 2026-03-28 | **Phase 5 complete** | Added `/api/dashboard` with deep-linking & cost trend mapping. Created `daily_report.py` to automate end-of-day Slack reporting. MVP finished! |
| 2026-03-28 | **ML Brain Live** | Integrated live ML anomaly detection, removed mock CSV datasets, and implemented Business Guardrails for production safety. |
| 2026-03-28 | **Interactive Fix** | Fully resolved Slack integration 503/500 errors and wired final "Fix" buttons to live Boto3 remediation background tasks. |

---

##  Quick Start

```bash
# 1. Clone & enter
git clone https://github.com/Shaurya-34/Copium.git
cd Copium

# 2. Create venv & install deps
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt

# 3. Configure
copy .env.example .env
# Edit .env → paste your Slack webhook URL

# 4. Use in Python
from automation.slack.alert_service import AlertService
service = AlertService()
service.send_daily_summary(total_cost=1247.83, top_services=[("EC2", 487.50)])
```

---
