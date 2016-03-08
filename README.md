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
`
