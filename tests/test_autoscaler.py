from autoscaler import autoscaler, settings, workload
from .test_kubernetes_control import get_test_k8s
from .testing_utils import check_expected


class ClusterTest:

    def __init__(self):
        self.shutdown_nodes = []
        self.goals = []

    def shutdown_specified_node(self, node):
        self.shutdown_nodes.append(node)

    def add_new_node(self, goal):
        self.goals.append(goal)


class AutoscalerTest(autoscaler.Autoscaler):
    def __init__(self, options):
        self._options = options
        self._cluster = ClusterTest()
        self._k8s = get_test_k8s()
        self._non_critical_nodes = []

        self._add_slack_handler()


class TestAuotscaler(object):

    _autoscaler = AutoscalerTest(settings.settings())

    def test_update_nodes(self):
        nodes = self._autoscaler._get_non_critical_nodes()

        check_expected(
            self._autoscaler._update_nodes,
            [nodes, True],
            list,
            ['gke-prod-highmem-pool-custom-wwk5', 'gke-prod-highmem-pool-custom-wwk6']
        )
        assert str(self._autoscaler._k8s._v1.new_nodes) == """\
{'gke-prod-highmem-pool-custom-wwk5': {'api_version': 'v1',
 'kind': 'Node',
 'metadata': {'annotations': None,
              'cluster_name': None,
              'creation_timestamp': None,
              'deletion_grace_period_seconds': None,
              'deletion_timestamp': None,
              'finalizers': None,
              'generate_name': None,
              'generation': None,
              'labels': None,
              'name': 'gke-prod-highmem-pool-custom-wwk5',
              'namespace': None,
              'owner_references': None,
              'resource_version': None,
              'self_link': None,
              'uid': None},
 'spec': {'external_id': None,
          'pod_cidr': None,
          'provider_id': None,
          'unschedulable': True},
 'status': None}, 'gke-prod-highmem-pool-custom-wwk6': {'api_version': 'v1',
 'kind': 'Node',
 'metadata': {'annotations': None,
              'cluster_name': None,
              'creation_timestamp': None,
              'deletion_grace_period_seconds': None,
              'deletion_timestamp': None,
              'finalizers': None,
              'generate_name': None,
              'generation': None,
              'labels': None,
              'name': 'gke-prod-highmem-pool-custom-wwk6',
              'namespace': None,
              'owner_references': None,
              'resource_version': None,
              'self_link': None,
              'uid': None},
 'spec': {'external_id': None,
          'pod_cidr': None,
          'provider_id': None,
          'unschedulable': True},
 'status': None}}"""

    def test_update_unschedulable(self):
        self._autoscaler._goal = workload.schedule_goal(self._autoscaler._k8s, self._autoscaler._options)
        self._autoscaler._update_non_critical_node_list()

        check_expected(
            self._autoscaler._update_unschedulable,
            [],
            int,
            1
        )
        assert str(self._autoscaler._k8s._v1.new_nodes) == """\
{'gke-prod-highmem-pool-custom-wwk5': {'api_version': 'v1',
 'kind': 'Node',
 'metadata': {'annotations': None,
              'cluster_name': None,
              'creation_timestamp': None,
              'deletion_grace_period_seconds': None,
              'deletion_timestamp': None,
              'finalizers': None,
              'generate_name': None,
              'generation': None,
              'labels': None,
              'name': 'gke-prod-highmem-pool-custom-wwk5',
              'namespace': None,
              'owner_references': None,
              'resource_version': None,
              'self_link': None,
              'uid': None},
 'spec': {'external_id': None,
          'pod_cidr': None,
          'provider_id': None,
          'unschedulable': True},
 'status': None}, 'gke-prod-highmem-pool-custom-wwk6': {'api_version': 'v1',
 'kind': 'Node',
 'metadata': {'annotations': None,
              'cluster_name': None,
              'creation_timestamp': None,
              'deletion_grace_period_seconds': None,
              'deletion_timestamp': None,
              'finalizers': None,
              'generate_name': None,
              'generation': None,
              'labels': None,
              'name': 'gke-prod-highmem-pool-custom-wwk6',
              'namespace': None,
              'owner_references': None,
              'resource_version': None,
              'self_link': None,
              'uid': None},
 'spec': {'external_id': None,
          'pod_cidr': None,
          'provider_id': None,
          'unschedulable': True},
 'status': None}}"""

    def test_get_non_critical_nodes(self):
        result = self._autoscaler._get_non_critical_nodes()
        assert str(result) == """\
[X(metadata=X(name='gke-prod-highmem-pool-custom-wwk5'), spec=X(unschedulable=False), status=X(alloca\
table={'alpha.kubernetes.io/nvidia-gpu': '0', 'cpu': '2', 'memory': '13317664Ki', 'pods': '110'}, cap\
acity={'alpha.kubernetes.io/nvidia-gpu': '0', 'cpu': '2', 'memory': '13317664Ki', 'pods': '110'})), X\
(metadata=X(name='gke-prod-highmem-pool-custom-wwk6'), spec=X(unschedulable=True), status=X(allocatab\
le={'alpha.kubernetes.io/nvidia-gpu': '0', 'cpu': '2', 'memory': '13317664Ki', 'pods': '110'}, capaci\
ty={'alpha.kubernetes.io/nvidia-gpu': '0', 'cpu': '2', 'memory': '13317664Ki', 'pods': '110'}))]"""\
        or str(result) == """\
[X(metadata=X(name='gke-prod-highmem-pool-custom-wwk6'), spec=X(unschedulable=True), status=X(alloca\
table={'alpha.kubernetes.io/nvidia-gpu': '0', 'cpu': '2', 'memory': '13317664Ki', 'pods': '110'}, cap\
acity={'alpha.kubernetes.io/nvidia-gpu': '0', 'cpu': '2', 'memory': '13317664Ki', 'pods': '110'})), X\
(metadata=X(name='gke-prod-highmem-pool-custom-wwk5'), spec=X(unschedulable=False), status=X(allocatab\
le={'alpha.kubernetes.io/nvidia-gpu': '0', 'cpu': '2', 'memory': '13317664Ki', 'pods': '110'}, capaci\
ty={'alpha.kubernetes.io/nvidia-gpu': '0', 'cpu': '2', 'memory': '13317664Ki', 'pods': '110'}))]"""

    def test_update_non_critical_node_list(self):
        self._autoscaler._update_non_critical_node_list()
        assert str(self._autoscaler._non_critical_nodes) == """\
[X(metadata=X(name='gke-prod-highmem-pool-custom-wwk5'), spec=X(unschedulable=False), status=X(alloca\
table={'alpha.kubernetes.io/nvidia-gpu': '0', 'cpu': '2', 'memory': '13317664Ki', 'pods': '110'}, cap\
acity={'alpha.kubernetes.io/nvidia-gpu': '0', 'cpu': '2', 'memory': '13317664Ki', 'pods': '110'})), X\
(metadata=X(name='gke-prod-highmem-pool-custom-wwk6'), spec=X(unschedulable=True), status=X(allocatab\
le={'alpha.kubernetes.io/nvidia-gpu': '0', 'cpu': '2', 'memory': '13317664Ki', 'pods': '110'}, capaci\
ty={'alpha.kubernetes.io/nvidia-gpu': '0', 'cpu': '2', 'memory': '13317664Ki', 'pods': '110'}))]"""\
        or str(self._autoscaler._non_critical_nodes) == """\
[X(metadata=X(name='gke-prod-highmem-pool-custom-wwk6'), spec=X(unschedulable=True), status=X(alloca\
table={'alpha.kubernetes.io/nvidia-gpu': '0', 'cpu': '2', 'memory': '13317664Ki', 'pods': '110'}, cap\
acity={'alpha.kubernetes.io/nvidia-gpu': '0', 'cpu': '2', 'memory': '13317664Ki', 'pods': '110'})), X\
(metadata=X(name='gke-prod-highmem-pool-custom-wwk5'), spec=X(unschedulable=False), status=X(allocatab\
le={'alpha.kubernetes.io/nvidia-gpu': '0', 'cpu': '2', 'memory': '13317664Ki', 'pods': '110'}, capaci\
ty={'alpha.kubernetes.io/nvidia-gpu': '0', 'cpu': '2', 'memory': '13317664Ki', 'pods': '110'}))]"""

    def test_resize_for_new_nodes(self):
        autoscaler.populate = lambda x: None
        autoscaler.confirm = lambda x: True
        self._autoscaler._resize_for_new_nodes(wait_time=0)
        assert self._autoscaler._cluster.goals == [15]

    def test_shutdown_empty_nodes(self):
        self._autoscaler._shutdown_empty_nodes()
        assert self._autoscaler._cluster.shutdown_nodes == ['gke-prod-highmem-pool-custom-wwk6']

    def test_scale(self):
        autoscaler_settings = settings.settings()
        autoscaler_settings.test_cloud = False
        self._autoscaler = AutoscalerTest(autoscaler_settings)
        autoscaler.populate = lambda x: None
        autoscaler.confirm = lambda x: True
        self._autoscaler.scale()
        assert self._autoscaler._cluster.goals == []
        assert self._autoscaler._cluster.shutdown_nodes == ['gke-prod-highmem-pool-custom-wwk6']
