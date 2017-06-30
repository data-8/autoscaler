from autoscaler import kubernetes_control, settings
from .core_v1_api_test import CoreV1ApiTest
from .testing_utils import check_expected


class TestKubernetesControl:

    def test_get_image_urls(self):
        k8s = self.get_test_k8s()
        check_expected(k8s._get_image_urls, [], set, {
            'gcr.io/data-8/jupyterhub-k8s-user-demo:e283f2f',
            'gcr.io/data-8/jupyterhub-k8s-user-stat28:36b2c48',
            'yuvipanda/jupyterhub-k8s-singleuser-sample:v0.2',
            'gcr.io/data-8/jupyterhub-k8s-user-prob140:36b2c48',
            'gcr.io/data-8/jupyterhub-k8s-user-datahub:b1ded78'
        })

    def test_get_pods(self):
        k8s = self.get_test_k8s()
        assert len(k8s._pods) == 28

    def test_get_nodes(self):
        k8s = self.get_test_k8s()
        assert len(k8s.get_nodes()) == 15

    def test_get_critical_node_names(self):
        k8s = self.get_test_k8s()
        check_expected(k8s.get_critical_node_names, [], list, [
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

    def get_test_k8s(self):
        # Creates a new `k8s_control` object that has its API
        # components replaced with test objects with custom set values

        options = settings.settings()
        options.context = options.default_context
        kubernetes_control.client.CoreV1Api = CoreV1ApiTest
        kubernetes_control.k8s_control._configure_new_context = lambda x, y: options.context
        k8s = kubernetes_control.k8s_control(options)
        return k8s
