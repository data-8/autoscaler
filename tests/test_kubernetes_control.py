import pytest

from copy import deepcopy
from autoscaler import kubernetes_control, kubernetes_control_test, settings
from .core_v1_api_test import CoreV1ApiTest
from .testing_utils import check_expected


def get_test_k8s():
    # Creates a new `k8s_control` object that has its API
    # components replaced with test objects with custom set values

    options = settings.settings()
    options.context = options.default_context
    kubernetes_control.client.CoreV1Api = CoreV1ApiTest
    kubernetes_control.k8s_control._configure_new_context = lambda x, y: options.context
    k8s = kubernetes_control.k8s_control(options)
    return k8s


def get_test_k8s_test():
    # Creates a new `k8s_control_test` object that has its API
    # components replaced with test objects with custom set values

    options = settings.settings()
    options.context = options.default_context
    kubernetes_control_test.client.CoreV1Api = CoreV1ApiTest
    kubernetes_control_test.k8s_control_test._configure_new_context = lambda x, y: options.context
    k8s = kubernetes_control_test.k8s_control_test(options)
    return k8s


class TestKubernetesControl:

    _k8s = get_test_k8s()
    _k8s_test = get_test_k8s_test()

    def test_get_image_urls(self):
        expected = {
            'gcr.io/data-8/jupyterhub-k8s-user-demo:e283f2f',
            'gcr.io/data-8/jupyterhub-k8s-user-stat28:36b2c48',
            'yuvipanda/jupyterhub-k8s-singleuser-sample:v0.2',
            'gcr.io/data-8/jupyterhub-k8s-user-prob140:36b2c48',
            'gcr.io/data-8/jupyterhub-k8s-user-datahub:b1ded78'
        }
        check_expected(self._k8s._get_image_urls, [], set, expected)
        check_expected(self._k8s.get_image_urls, [], set, expected)

    def test_get_pods(self):
        assert len(self._k8s._get_pods()) == 28

    def test_get_nodes(self):
        assert len(self._k8s._get_nodes()) == 17
        assert len(self._k8s.get_nodes()) == 17

    def test_get_critical_node_names(self):
        check_expected(self._k8s.get_critical_node_names, [], list, [
            'gke-prod-highmem-pool-0df1a536-wvjl',
            'gke-prod-highmem-pool-0df1a536-tfrz',
            'gke-prod-highmem-pool-0df1a536-j3m8',
            'gke-prod-highmem-pool-0df1a536-0zc0',
            'gke-prod-highmem-pool-0df1a536-f31s',
            'gke-prod-highmem-pool-0df1a536-17c7',
            'gke-prod-highmem-pool-0df1a536-nxzf',
            'gke-prod-highmem-pool-0df1a536-qgpb',
            'gke-prod-highmem-pool-0df1a536-2zbs',
            'gke-prod-highmem-pool-0df1a536-wwk5',
            'gke-prod-highmem-pool-0df1a536-8pbd',
            'gke-prod-highmem-pool-0df1a536-kz7z',
            'gke-prod-highmem-pool-0df1a536-n3wb',
            'gke-prod-highmem-pool-0df1a536-q8g0',
            'gke-prod-highmem-pool-0df1a536-v0kp'
        ])

    @pytest.mark.parametrize("node_name,test_value,expected", [
        ('hello-world-node', True, """\
{'api_version': 'v1',
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
              'name': 'hello-world-node',
              'namespace': None,
              'owner_references': None,
              'resource_version': None,
              'self_link': None,
              'uid': None},
 'spec': {'external_id': None,
          'pod_cidr': None,
          'provider_id': None,
          'unschedulable': True},
 'status': None}"""),
        ('another-fun-node', False, """\
{'api_version': 'v1',
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
              'name': 'another-fun-node',
              'namespace': None,
              'owner_references': None,
              'resource_version': None,
              'self_link': None,
              'uid': None},
 'spec': {'external_id': None,
          'pod_cidr': None,
          'provider_id': None,
          'unschedulable': False},
 'status': None}""")
    ])
    def test_set_unschedulable(self, node_name, test_value, expected):
        k8s = deepcopy(self._k8s)
        k8s.set_unschedulable(node_name, value=test_value)
        assert node_name in k8s._v1.new_nodes
        assert str(k8s._v1.new_nodes[node_name]) == expected

    def test_get_total_cluster_memory_usage(self):
        check_expected(self._k8s.get_total_cluster_memory_usage, [], int, 33822867456)

    def test_get_total_cluster_memory_capacity(self):
        check_expected(self._k8s.get_total_cluster_memory_capacity, [], int, 204559319040)

    def test_get_cluster_name(self):
        check_expected(self._k8s.get_cluster_name, [], str, 'prod')

    def test_get_num_schedulable(self):
        check_expected(self._k8s.get_num_schedulable, [], int, 1)

    def test_get_num_unschedulable(self):
        check_expected(self._k8s.get_num_unschedulable, [], int, 2)

    def test_is_test(self):
        self._k8s._test = True
        check_expected(self._k8s.is_test, [], bool, True)
        self._k8s._test = False
        check_expected(self._k8s.is_test, [], bool, False)

    def test_get_min_utilization(self):
        check_expected(self._k8s.get_min_utilization, [], float, 0.65)

    def test_get_max_utilization(self):
        check_expected(self._k8s.get_max_utilization, [], float, 0.85)

    def test_show_nodes_status(self, capsys):
        self._k8s.show_nodes_status()
        out, err = capsys.readouterr()
        assert out == """\
Node name \t\t Num of pods on node \t Schedulable? \t Preemptible?
gke-prod-highmem-pool-0df1a536-0zc0\t2\tU\tN
gke-prod-highmem-pool-0df1a536-17c7\t2\tS\tN
gke-prod-highmem-pool-0df1a536-2zbs\t2\tS\tN
gke-prod-highmem-pool-0df1a536-8pbd\t1\tS\tN
gke-prod-highmem-pool-0df1a536-f31s\t2\tS\tN
gke-prod-highmem-pool-0df1a536-j3m8\t2\tS\tN
gke-prod-highmem-pool-0df1a536-kz7z\t1\tS\tN
gke-prod-highmem-pool-0df1a536-n3wb\t1\tS\tN
gke-prod-highmem-pool-0df1a536-nxzf\t2\tS\tN
gke-prod-highmem-pool-0df1a536-q8g0\t1\tS\tN
gke-prod-highmem-pool-0df1a536-qgpb\t1\tS\tN
gke-prod-highmem-pool-0df1a536-tfrz\t2\tS\tN
gke-prod-highmem-pool-0df1a536-v0kp\t1\tS\tN
gke-prod-highmem-pool-0df1a536-wvjl\t6\tS\tN
gke-prod-highmem-pool-0df1a536-wwk5\t2\tS\tN
gke-prod-highmem-pool-custom-wwk5\t0\tS\tP
gke-prod-highmem-pool-custom-wwk6\t0\tU\tP
"""

    def test_get_pods_number_on_node(self):
        pods_number = [2, 2, 2, 1, 2, 2, 1, 1, 2, 1, 1, 2, 1, 6, 2, 0, 0]
        i = 0
        for node in self._k8s.get_nodes():
            assert self._k8s.get_pods_number_on_node(node) == pods_number[i]
            i += 1

    @pytest.mark.parametrize("node_name,test_value", [
            ('hello-world-node', True),
            ('another-fun-node', False)
        ])
    def test_set_unschedulable_test_k8s(self, node_name, test_value):
        k8s_test = deepcopy(self._k8s_test)
        k8s_test.set_unschedulable(node_name, value=test_value)
        assert k8s_test.is_test() is True
        assert node_name not in k8s_test._v1.new_nodes
