from autoscaler import autoscaler, settings
from .test_kubernetes_control import get_test_k8s
from .testing_utils import check_expected


class AutoscalerTest(autoscaler.Autoscaler):
    def __init__(self, options):
        self._options = options
        self._cluster = None
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
            ['gke-prod-highmem-pool-custom-wwk5']
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
 'status': None}}"""
