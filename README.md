# Prometheus Marathon App Exporter

Proxy server converting marathon application metrics to prometheus metrics.

## Using Docker

You can deploy this exporter using the [bergerx/prom-marathon-app-exporter](https://registry.hub.docker.com/u/bergerx/prom-marathon-app-exporter/) Docker image.

For example:

```bash
docker run -d -e MARATHON_URL=http://leader.mesos:8080/ -p 9099:9099 bergerx/prom-marathon-app-exporter
# try it
# curl http://localhost:9099/metrics
```

## Deploy on Marathon

You can deploy this exporter on marathon via following curl command:

```bash
curl -XPOST -H 'Content-Type: application/json;' leader.mesos:8080/v2/apps -d '{
  "cpus": 0.01,
  "mem": 50,
  "id": "/prom/marathon-app-exporter",
  "instances": 1,
  "env": {
    "MARATHON_URL": "http://leader.mesos:8080/"
  },
  "container": {
    "type": "DOCKER",
    "docker": {
      "image": "bergerx/prom-marathon-app-exporter",
      "network": "BRIDGE",
      "portMappings": [{"containerPort": 9099}]
    }
  },
  "healthChecks": [{"protocol": "HTTP", "path": "/metrics"}]
}'
```

## Scrape config on prometheus

A sample prometheus target yaml example if you already have have mesos-dns:

```yaml
  - job_name: 'marathon-app'
    dns_sd_configs:
      - names: ['_marathon-app-exporter-prom._tcp.marathon.mesos']
```

## Alerts on prometheus

And some sample alert rules for firing alerts from Prometheus:

```
ALERT MarathonAppIsRunningOnReducedCapacity
  IF sum(marathon_apps_instances{job="marathon-app"} - marathon_apps_tasksRunning{job="marathon-app"}) by (id) > 0
  FOR 30m
  SUMMARY "Marathon app hass less instances that it should have."
  DESCRIPTION "Check why this app hass less instancess that it should heve. Possibly a cancelled deployment or resource starvation issue."

ALERT MarathonAppIsNotHealthy
  IF sum(
       marathon_apps_tasksHealthy{job="marathon-app"} > 0 and
       marathon_apps_instances{job="marathon-app"} > marathon_apps_tasksRunning{job="marathon-app"}
     ) by (id)
  FOR 10m
  SUMMARY "Marathon app does not have enough healthy instances."
  DESCRIPTION "Check if there is resource starvation or constraints forcing app to be installed a a specific node with problems."

ALERT MarathonAppCantGetSuitableOffers
  IF sum(marathon_queue_delay_overdue{job="marathon-app"} == 1) by (id)
  FOR 15m
  SUMMARY "No suitable offers for this app."
  DESCRIPTION "This app can't be scheduled to any suitable node, check constraints or any resource starvation."

ALERT MarathonAppDeploymentDelayed
  IF sum(
       marathon_queue_delay_timeLeftSeconds{job="marathon-app"} > 0 and
       marathon_queue_delay_overdue{job="marathon-app"} == 0
     ) by (id)
  FOR 30m
  SUMMARY "Delayed deployment."
  DESCRIPTION "Delayed deployment."

ALERT MarathonAppHasTasksWithOldConfig
  IF sum(
       marathon_apps_taskStats_totalSummary_stats_counts_running{job="marathon-app"} -
       marathon_apps_taskStats_withLatestConfig_stats_counts_running{job="marathon-app"} > 0
     ) by (id)
  FOR 30m
  SUMMARY "App with old instance configs."
  DESCRIPTION "There could be some deployments cancelled"
```