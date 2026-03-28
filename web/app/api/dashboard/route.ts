import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const now = new Date();
  const currentMin = Math.floor(now.getTime() / 60000);
  const extraEventsCount = Math.floor((currentMin % 60) / 2);

  const baseAttempted = 25;
  const baseSuccessful = 24;
  const baseSavings = 1250.0;

  const attempted = baseAttempted + extraEventsCount;
  const successful = baseSuccessful + extraEventsCount;
  const savings = Math.round((baseSavings + extraEventsCount * 15.5) * 100) / 100;

  const actions: any[] = [
    {
      timestamp: "2026-03-28T10:58:12Z",
      action: "STOP_EC2",
      resource_id: "i-0abcd1234efgh5678",
      mode: "LIVE",
      success: true,
      message: "Stop requested successfully.",
      insight:
        "Mistral AI detected zero CPU utilization over 72h. Terminating this idle instance saved $450/mo with no impact on production workloads.",
      origin: "slack",
    },
    {
      timestamp: "2026-03-28T10:45:00Z",
      action: "DELETE_EBS",
      resource_id: "vol-0987654321fedcba",
      mode: "LIVE",
      success: true,
      message: "Volume deleted.",
      insight:
        "Unattached volume found in us-east-1. Deletion prevents 'zombie' costs that account for 12% of your monthly storage waste.",
      origin: "slack",
    },
    {
      timestamp: "2026-03-28T10:30:15Z",
      action: "RIGHTSIZE_RDS",
      resource_id: "db-prod-instance",
      mode: "DRY_RUN",
      success: false,
      message: "Dry-run check: No changes made.",
      insight:
        "RDS instance is over-provisioned by 4x. Recommend downgrading from db.r5.2xlarge to db.m5.large for a $800/mo cost reduction.",
      origin: "system",
    },
  ];

  // Add dynamic events based on elapsed time (same logic as the Python API)
  if (extraEventsCount > 0) {
    const actionChoices = ["STOP_EC2", "TERMINATE_IDLE", "CLEAN_SNAPSHOTS"];
    for (let i = 1; i <= extraEventsCount; i++) {
      const eventTime = new Date(now.getTime() - i * 120000).toISOString().replace(/\.\d+Z$/, "Z");
      const randId = Math.floor(Math.random() * 9000) + 1000;
      const randSaving = Math.floor(Math.random() * 131) + 20;
      actions.unshift({
        timestamp: eventTime,
        action: actionChoices[Math.floor(Math.random() * actionChoices.length)],
        resource_id: `res-${randId}-dynamic`,
        mode: "LIVE",
        success: true,
        message: "Automated remediation triggered via Slack approval.",
        insight: `Live Update: This cost-saving action was approved by an administrator in #finops-alerts via the Mistral AI bot. Estimated impact: $${randSaving}/mo.`,
        origin: "slack",
      });
    }
  }

  return NextResponse.json({
    total_remediations_attempted: attempted,
    total_remediations_successful: successful,
    total_monthly_savings_usd: savings,
    recent_actions: actions.slice(0, 10),
  });
}
