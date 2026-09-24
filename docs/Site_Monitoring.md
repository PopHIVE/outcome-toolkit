## Outcome Toolkit Site-Health Monitoring

We have a three part architecture which provides an alert when an intermittent health check detects a problem in the site. This architecture consists of:

- A site uptime monitor
- A Slack channel dedicated to site-monitoring alerts
- A Slack app configured to post to that channel

The Slack app is configured to post to the site-monitor channel when it detects a change in the availability of the site. A change in availability is defined as a ping to the site returning anything other than a 200 response.

When a change is detected, the Slack app posts an alert in the Slack channel. The alert should notify members of the channel even if they are set to do-not-disturb or away.

**Note:** This monitoring stack was previously hosted on the original developers' internal tooling and Slack workspace and will need to be re-established with your organization's equivalent tools.
