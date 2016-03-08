from marathon import MarathonClient
from marathon.util import to_snake_case
from prometheus_client.core import GaugeMetricFamily


class MarathonAppCollector(object):
    APP_ATTIBUTES = (
        "instances",
        "cpus",
        "mem",
        "disk",
        "backoffSeconds",
        "backoffFactor",
        "maxLaunchDelaySeconds",
        "container.docker.privileged",
        "container.docker.forcePullImage",
        "healthChecks.gracePeriodSeconds",
        "healthChecks.intervalSeconds",
        "healthChecks.maxConsecutiveFailures",
        "healthChecks.timeoutSeconds",
        "upgradeStrategy.minimumHealthCapacity",
        "upgradeStrategy.maximumOverCapacity",
        "tasksStaged",
        "tasksRunning",
        "tasksHealthy",
        "tasksUnhealthy",
        "taskStats.startedAfterLastScaling.stats.counts.staged",
        "taskStats.startedAfterLastScaling.stats.counts.running",
        "taskStats.startedAfterLastScaling.stats.counts.healthy",
        "taskStats.startedAfterLastScaling.stats.lifeTime.averageSeconds",
        "taskStats.startedAfterLastScaling.stats.lifeTime.medianSeconds",
        "taskStats.withLatestConfig.stats.counts.staged",
        "taskStats.withLatestConfig.stats.counts.running",
        "taskStats.withLatestConfig.stats.counts.healthy",
        "taskStats.withLatestConfig.stats.lifeTime.averageSeconds",
        "taskStats.withLatestConfig.stats.lifeTime.medianSeconds",
        "taskStats.totalSummary.stats.counts.staged",
        "taskStats.totalSummary.stats.counts.running",
        "taskStats.totalSummary.stats.counts.healthy",
        "taskStats.totalSummary.stats.lifeTime.averageSeconds",
        "taskStats.totalSummary.stats.lifeTime.medianSeconds",
    )
    QUEUE_ATTRIBUTES = (
        "count",
        "delay.overdue",
        "delay.timeLeftSeconds",
    )

    def __init__(self, marathon_url=None):
        self.client = MarathonClient(marathon_url)

    def collect(self):
        result_dict = {}
        apps = self.client.list_apps(embed_task_stats=True)
        for app_attribute in self.APP_ATTIBUTES:
            metric_family = GaugeMetricFamily(
                self.get_metric_key(app_attribute, 'apps'),
                documentation='from v2/apps?embed=apps.taskStats value of %s' % app_attribute,
                labels=["id"])
            for app in apps:
                labels = [app.id]
                value = self.get_metric_value(app_attribute, app)
                if value is None:
                    continue
                metric_family.add_metric(labels, value)
            yield metric_family
        queue = self.client.list_queue()
        for queue_attribute in self.QUEUE_ATTRIBUTES:
            metric_family = GaugeMetricFamily(
                self.get_metric_key(queue_attribute, 'queue'),
                documentation='from v2/queue value of %s' % queue_attribute,
                labels=["id"])
            for queue_item in queue:
                labels = [queue_item.app.id]
                value = self.get_metric_value(queue_attribute, queue_item)
                if value is None:
                    continue
                metric_family.add_metric(labels, value)
            yield metric_family

    @classmethod
    def get_metric_value(cls, key, obj):
        if '.' in key:
            key_current, key_rest = key.split('.', 1)
            sub_obj = getattr(obj, to_snake_case(key_current), None)
            if sub_obj is None:
                return None
            return cls.get_metric_value(key_rest, sub_obj)
        return getattr(obj, to_snake_case(key), None)

    @classmethod
    def get_metric_key(cls, key, obj_type):
        return "marathon_%s_%s" % (obj_type, key.replace('.', '_'))

    @classmethod
    def generate_metric(cls, key, obj, obj_type, labels, value):
        return metric_family
