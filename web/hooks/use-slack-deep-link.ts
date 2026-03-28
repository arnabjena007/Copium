"use client";

import { useCallback } from "react";

/**
 * Hook to handle Slack deep linking with a graceful web fallback.
 * Slack Protocol: slack://channel?team={TEAM_ID}&id={CHANNEL_ID}
 * Web Redirect: https://slack.com/app_redirect?channel={CHANNEL_ID}
 */
export function useSlackDeepLink() {
  const openInSlack = useCallback((teamId: string, channelId: string) => {
    const slackProtocol = `slack://channel?team=${teamId}&id=${channelId}`;
    const slackWebUrl = `https://slack.com/app_redirect?channel=${channelId}`;

    // Try to open the Slack desktop app
    const opened = window.open(slackProtocol, "_self");

    // Fallback logic: check if the app opened or if we should redirect to web
    // Note: window.open returns null if the protocol isn't handled or if it's blocked, 
    // but browser behaviors vary. A safer approach for deep links is to set a timeout.
    const start = Date.now();
    const timeout = setTimeout(() => {
      // If the app didn't open and pull focus within 1.5 seconds, redirect to web
      if (Date.now() - start < 2000) {
        window.open(slackWebUrl, "_blank");
      }
    }, 1500);

    // If the page visibility changes, it means the app likely opened
    const handleVisibilityChange = () => {
      clearTimeout(timeout);
      window.removeEventListener("visibilitychange", handleVisibilityChange);
    };
    window.addEventListener("visibilitychange", handleVisibilityChange);
  }, []);

  return { openInSlack };
}
