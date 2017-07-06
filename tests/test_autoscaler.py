from autoscaler import autoscaler, settings, workload
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
 'status': None}}"""

    def test_get_non_critical_nodes(self):
        result = self._autoscaler._get_non_critical_nodes()
        assert str(result) == """[X(apiVersion='v1', kind='Node', metadata=X(annotations=X(_0='[]', _1\
='true'), creationTimestamp='2017-06-10T00:05:33Z', labels=X(_0='amd64', _1='n1-highmem-2', _2='linux',\
 _3='highmem-pool', _4='us-central1', _5='us-central1-a', _6='gke-prod-highmem-pool-custom-wwk5'), name\
='gke-prod-highmem-pool-custom-wwk5', namespace='', resourceVersion='63739590', selfLink='/api/v1/nodesg\
ke-prod-highmem-pool-custom-wwk5', uid='631f9582-3514-11e7-8de1-42010af0002a'), spec=X(unschedulable=Fal\
se, externalID='8408403029803394640', podCIDR='10.44.21.0/24', providerID='gce://data-8/us-central1-a/gk\
e-prod-highmem-pool-custom-wwk5'), status=X(addresses=[X(address='10.128.0.11', type='InternalIP'), X(ad\
dress='35.188.39.251', type='ExternalIP'), X(address='gke-prod-highmem-pool-custom-wwk5', type='Hostname\
')], allocatable={'alpha.kubernetes.io/nvidia-gpu': '0', 'cpu': '2', 'memory': '13317664Ki', 'pods': '11\
0'}, capacity={'alpha.kubernetes.io/nvidia-gpu': '0', 'cpu': '2', 'memory': '13317664Ki', 'pods': '110'}\
, conditions=[X(lastHeartbeatTime='2017-05-10T00:06:10Z', lastTransitionTime='2017-05-10T00:06:10Z', mes\
sage='RouteController created a route', reason='RouteCreated', status='False', type='NetworkUnavailable'\
), X(lastHeartbeatTime='2017-06-30T19:15:35Z', lastTransitionTime='2017-05-10T00:05:33Z', message='kubel\
et has sufficient disk space available', reason='KubeletHasSufficientDisk', status='False', type='OutOfD\
isk'), X(lastHeartbeatTime='2017-06-30T19:15:35Z', lastTransitionTime='2017-05-10T00:05:33Z', message='k\
ubelet has sufficient memory available', reason='KubeletHasSufficientMemory', status='False', type='Memo\
ryPressure'), X(lastHeartbeatTime='2017-06-30T19:15:35Z', lastTransitionTime='2017-05-10T00:05:33Z', mes\
sage='kubelet has no disk pressure', reason='KubeletHasNoDiskPressure', status='False', type='DiskPressu\
re'), X(lastHeartbeatTime='2017-06-30T19:15:35Z', lastTransitionTime='2017-05-10T00:05:53Z', message='ku\
belet is posting ready status. AppArmor enabled', reason='KubeletReady', status='True', type='Ready')], \
daemonEndpoints=X(kubeletEndpoint=X(Port=10250)), images=[X(names=['gcr.io/data-8/jupyterhub-k8s-user-st\
at28:36b2c48'], sizeBytes=5695023067), X(names=['gcr.io/data-8/jupyterhub-k8s-user-datahub:b1ded78'], si\
zeBytes=5039711380), X(names=['gcr.io/data-8/jupyterhub-k8s-user-prob140:36b2c48'], sizeBytes=5037787764\
), X(names=['gcr.io/data-8/jupyterhub-k8s-user-demo:e283f2f'], sizeBytes=1377023691), X(names=['yuvipand\
a/jupyterhub-k8s-hub:v94ff73b'], sizeBytes=505222458), X(names=['yuvipanda/jupyterhub-k8s-hub:v0.2'], si\
zeBytes=504660430), X(names=['gcr.io/google_containers/fluentd-gcp:1.28.1'], sizeBytes=328351788), X(nam\
es=['gcr.io/data-8/jupyterhub-k8s-proxy:8bc523b'], sizeBytes=267538966), X(names=['gcr.io/google_contain\
ers/heapster:v1.2.0'], sizeBytes=177836395), X(names=['gcr.io/google_containers/kube-proxy:697a993392e4f\
1c74fc6879c59c068e6'], sizeBytes=173531383), X(names=['gcr.io/google_containers/kubernetes-dashboard-amd\
64:v1.5.0'], sizeBytes=88896666), X(names=['prom/prometheus:v1.5.2'], sizeBytes=79601765), X(names=['gcr\
.io/google_containers/cluster-proportional-autoscaler-amd64:1.1.0-r2'], sizeBytes=47349029), X(names=['g\
cr.io/google_containers/kubedns-amd64:1.9'], sizeBytes=46998769), X(names=['gcr.io/google_containers/kub\
e-state-metrics:v0.4.1'], sizeBytes=45663385), X(names=['gcr.io/google_containers/addon-resizer:1.7'], s\
izeBytes=38983736), X(names=['prom/alertmanager:v0.5.1'], sizeBytes=15738195), X(names=['prom/node-expor\
ter:v0.13.0'], sizeBytes=14556305), X(names=['gcr.io/google_containers/dnsmasq-metrics-amd64:1.0.1'], si\
zeBytes=13183180), X(names=['gcr.io/google_containers/exechealthz-amd64:1.2'], sizeBytes=8374840), X(nam\
es=['gcr.io/google_containers/defaultbackend:1.0'], sizeBytes=7510068), X(names=['gcr.io/google_containe\
rs/kube-dnsmasq-amd64:1.4.1'], sizeBytes=5134257), X(names=['jimmidyson/configmap-reload:v0.1'], sizeByt\
es=4780960), X(names=['gcr.io/google_containers/pause-amd64:3.0'], sizeBytes=746888)], nodeInfo=X(archit\
ecture='amd64', bootID='80bbf615-7e48-4606-94a4-5a0e18921c7d', containerRuntimeVersion='docker://1.11.2'\
, kernelVersion='4.4.21+', kubeProxyVersion='v1.5.2', kubeletVersion='v1.5.2', machineID='794dbc33cc8276\
eac13ed0f167a79121', operatingSystem='linux', osImage='Google Container-VM Image', systemUUID='794DBC33-\
CC82-76EA-C13E-D0F167A79121'), volumesAttached=[X(devicePath='/dev/disk/by-id/google-gke-prod-49ca6b0d-d\
yna-pvc-04fe4505-2936-11e7-b551-42010af0002a', name='kubernetes.io/gce-pd/gke-prod-49ca6b0d-dyna-pvc-04f\
e4505-2936-11e7-b551-42010af0002a'), X(devicePath='/dev/disk/by-id/google-gke-prod-49ca6b0d-dyna-pvc-04f\
edb8a-2936-11e7-b551-42010af0002a', name='kubernetes.io/gce-pd/gke-prod-49ca6b0d-dyna-pvc-04fedb8a-2936-\
11e7-b551-42010af0002a')], volumesInUse=['kubernetes.io/gce-pd/gke-prod-49ca6b0d-dyna-pvc-04fedb8a-2936-\
11e7-b551-42010af0002a', 'kubernetes.io/gce-pd/gke-prod-49ca6b0d-dyna-pvc-04fe4505-2936-11e7-b551-42010a\
f0002a']))]"""

    def test_update_non_critical_node_list(self):
        self._autoscaler._update_non_critical_node_list()
        assert str(self._autoscaler._non_critical_nodes) == """\
[X(apiVersion='v1', kind='Node', metadata=X(annotations=X(_0='[]', _1='true'), creationTimestamp='2017-0\
6-10T00:05:33Z', labels=X(_0='amd64', _1='n1-highmem-2', _2='linux', _3='highmem-pool', _4='us-central1'\
, _5='us-central1-a', _6='gke-prod-highmem-pool-custom-wwk5'), name='gke-prod-highmem-pool-custom-wwk5',\
 namespace='', resourceVersion='63739590', selfLink='/api/v1/nodesgke-prod-highmem-pool-custom-wwk5', ui\
d='631f9582-3514-11e7-8de1-42010af0002a'), spec=X(unschedulable=False, externalID='8408403029803394640',\
 podCIDR='10.44.21.0/24', providerID='gce://data-8/us-central1-a/gke-prod-highmem-pool-custom-wwk5'), st\
atus=X(addresses=[X(address='10.128.0.11', type='InternalIP'), X(address='35.188.39.251', type='External\
IP'), X(address='gke-prod-highmem-pool-custom-wwk5', type='Hostname')], allocatable={'alpha.kubernetes.i\
o/nvidia-gpu': '0', 'cpu': '2', 'memory': '13317664Ki', 'pods': '110'}, capacity={'alpha.kubernetes.io/n\
vidia-gpu': '0', 'cpu': '2', 'memory': '13317664Ki', 'pods': '110'}, conditions=[X(lastHeartbeatTime='20\
17-05-10T00:06:10Z', lastTransitionTime='2017-05-10T00:06:10Z', message='RouteController created a route\
', reason='RouteCreated', status='False', type='NetworkUnavailable'), X(lastHeartbeatTime='2017-06-30T19\
:15:35Z', lastTransitionTime='2017-05-10T00:05:33Z', message='kubelet has sufficient disk space availabl\
e', reason='KubeletHasSufficientDisk', status='False', type='OutOfDisk'), X(lastHeartbeatTime='2017-06-3\
0T19:15:35Z', lastTransitionTime='2017-05-10T00:05:33Z', message='kubelet has sufficient memory availabl\
e', reason='KubeletHasSufficientMemory', status='False', type='MemoryPressure'), X(lastHeartbeatTime='20\
17-06-30T19:15:35Z', lastTransitionTime='2017-05-10T00:05:33Z', message='kubelet has no disk pressure', \
reason='KubeletHasNoDiskPressure', status='False', type='DiskPressure'), X(lastHeartbeatTime='2017-06-30\
T19:15:35Z', lastTransitionTime='2017-05-10T00:05:53Z', message='kubelet is posting ready status. AppArm\
or enabled', reason='KubeletReady', status='True', type='Ready')], daemonEndpoints=X(kubeletEndpoint=X(P\
ort=10250)), images=[X(names=['gcr.io/data-8/jupyterhub-k8s-user-stat28:36b2c48'], sizeBytes=5695023067)\
, X(names=['gcr.io/data-8/jupyterhub-k8s-user-datahub:b1ded78'], sizeBytes=5039711380), X(names=['gcr.io\
/data-8/jupyterhub-k8s-user-prob140:36b2c48'], sizeBytes=5037787764), X(names=['gcr.io/data-8/jupyterhub\
-k8s-user-demo:e283f2f'], sizeBytes=1377023691), X(names=['yuvipanda/jupyterhub-k8s-hub:v94ff73b'], size\
Bytes=505222458), X(names=['yuvipanda/jupyterhub-k8s-hub:v0.2'], sizeBytes=504660430), X(names=['gcr.io/\
google_containers/fluentd-gcp:1.28.1'], sizeBytes=328351788), X(names=['gcr.io/data-8/jupyterhub-k8s-pro\
xy:8bc523b'], sizeBytes=267538966), X(names=['gcr.io/google_containers/heapster:v1.2.0'], sizeBytes=1778\
36395), X(names=['gcr.io/google_containers/kube-proxy:697a993392e4f1c74fc6879c59c068e6'], sizeBytes=1735\
31383), X(names=['gcr.io/google_containers/kubernetes-dashboard-amd64:v1.5.0'], sizeBytes=88896666), X(n\
ames=['prom/prometheus:v1.5.2'], sizeBytes=79601765), X(names=['gcr.io/google_containers/cluster-proport\
ional-autoscaler-amd64:1.1.0-r2'], sizeBytes=47349029), X(names=['gcr.io/google_containers/kubedns-amd64\
:1.9'], sizeBytes=46998769), X(names=['gcr.io/google_containers/kube-state-metrics:v0.4.1'], sizeBytes=4\
5663385), X(names=['gcr.io/google_containers/addon-resizer:1.7'], sizeBytes=38983736), X(names=['prom/al\
ertmanager:v0.5.1'], sizeBytes=15738195), X(names=['prom/node-exporter:v0.13.0'], sizeBytes=14556305), X\
(names=['gcr.io/google_containers/dnsmasq-metrics-amd64:1.0.1'], sizeBytes=13183180), X(names=['gcr.io/g\
oogle_containers/exechealthz-amd64:1.2'], sizeBytes=8374840), X(names=['gcr.io/google_containers/default\
backend:1.0'], sizeBytes=7510068), X(names=['gcr.io/google_containers/kube-dnsmasq-amd64:1.4.1'], sizeBy\
tes=5134257), X(names=['jimmidyson/configmap-reload:v0.1'], sizeBytes=4780960), X(names=['gcr.io/google_\
containers/pause-amd64:3.0'], sizeBytes=746888)], nodeInfo=X(architecture='amd64', bootID='80bbf615-7e48\
-4606-94a4-5a0e18921c7d', containerRuntimeVersion='docker://1.11.2', kernelVersion='4.4.21+', kubeProxyV\
ersion='v1.5.2', kubeletVersion='v1.5.2', machineID='794dbc33cc8276eac13ed0f167a79121', operatingSystem=\
'linux', osImage='Google Container-VM Image', systemUUID='794DBC33-CC82-76EA-C13E-D0F167A79121'), volume\
sAttached=[X(devicePath='/dev/disk/by-id/google-gke-prod-49ca6b0d-dyna-pvc-04fe4505-2936-11e7-b551-42010\
af0002a', name='kubernetes.io/gce-pd/gke-prod-49ca6b0d-dyna-pvc-04fe4505-2936-11e7-b551-42010af0002a'), \
X(devicePath='/dev/disk/by-id/google-gke-prod-49ca6b0d-dyna-pvc-04fedb8a-2936-11e7-b551-42010af0002a', n\
ame='kubernetes.io/gce-pd/gke-prod-49ca6b0d-dyna-pvc-04fedb8a-2936-11e7-b551-42010af0002a')], volumesInU\
se=['kubernetes.io/gce-pd/gke-prod-49ca6b0d-dyna-pvc-04fedb8a-2936-11e7-b551-42010af0002a', 'kubernetes.\
io/gce-pd/gke-prod-49ca6b0d-dyna-pvc-04fe4505-2936-11e7-b551-42010af0002a']))]"""
