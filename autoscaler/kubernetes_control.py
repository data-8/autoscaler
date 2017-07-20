#!/usr/bin/python3

"""Provides read and write access to Kubernetes API"""
import logging
import sys

from kubernetes import client, config

from .utils import get_pod_host_name, get_pod_memory_request, \
    get_node_memory_capacity, check_list_intersection

scale_logger = logging.getLogger("scale")
logging.getLogger("kubernetes").setLevel(logging.WARNING)


class k8s_control:

    """Provides read and write access to Kubernetes API,
    and environment settings, including goals for the
    cluster always use the node and pods status at the
    time it was initiated

    self._pods omits certain pods based on settings"""

    _test = False

    def __init__(self, options):
        """ Needs to be initialized with options as an
        instance of settings"""
        self._context = self._configure_new_context(options.context)
        self._options = options
        self._v1 = client.CoreV1Api()
        self._pods = self._get_pods()
        self._nodes = self._get_nodes()
        self._critical_node_names = self._get_critical_node_names()
        self._critical_node_number = len(self._critical_node_names)
        self._noncritical_nodes = list(
            filter(
                lambda node: node.metadata.name not in self._critical_node_names,
                self._nodes
            )
        )
        self._image_urls = self._get_image_urls()

    def _get_image_urls(self):
        result = set()
        for pod in self._pods:
            env = pod.spec.containers[0].env
            if env:
                for entry in env:
                    if entry.name == 'SINGLEUSER_IMAGE':
                        result.add(entry.value)
        return result

    def _configure_new_context(self, new_context):
        """ Loads .kube config to instantiate kubernetes
        with specified context"""
        contexts, _ = config.list_kube_config_contexts()
        try:
            contexts = [c['name'] for c in contexts]
            context_to_activate = list(
                filter(lambda context: new_context in context, contexts))
            assert len(context_to_activate) == 1  # avoid undefined behavior
            context_to_activate = context_to_activate[0]
        except (TypeError, IndexError):
            scale_logger.exception("Could not load context %s\n" % new_context)
            sys.exit(1)
        except AssertionError:
            scale_logger.fatal("Vague context specification")
            sys.exit(1)
        config.load_kube_config(context=context_to_activate)
        return context_to_activate

    def _get_nodes(self):
        """Return a list of v1.Node"""
        scale_logger.debug("Getting all nodes in the cluster")
        return self._v1.list_node().items

    def _get_pods(self):
        """Return a list of v1.Pod that needn't be omitted"""
        result = []
        scale_logger.debug("Getting all pods in all namespaces")
        pods = self._v1.list_pod_for_all_namespaces().items
        for pod in pods:
            if (not (check_list_intersection(self._options.omit_labels, pod.metadata.labels) or
                     pod.metadata.namespace in self._options.omit_namespaces)) and \
                    (pod.status.phase in ["Running", "Pending"]):
                result.append(pod)
        return result

    def show_nodes_status(self):
        """Print the status of all nodes in the cluster"""
        print(
            "Node name \t\t Num of pods on node \t Schedulable? \t Preemptible?")
        for node in self._nodes:
            print("%s\t%i\t%s\t%s" %
                  (node.metadata.name,
                   self.get_pods_number_on_node(node),
                   "U" if node.spec.unschedulable else "S",
                   "N" if node.metadata.name in self._critical_node_names else "P"
                   ))

    def set_unschedulable(self, node_name, value=True):
        """Set the spec key 'unschedulable'"""
        scale_logger.debug(
            "Setting %s node's unschedulable property to %r", node_name, value)
        assert node_name not in self._critical_node_names

        new_node = client.V1Node(
            api_version="v1",
            kind="Node",
            metadata=client.V1ObjectMeta(name=node_name),
            spec=client.V1NodeSpec(unschedulable=value)
        )
        # TODO: exception handling
        self._v1.patch_node(node_name, new_node)

    def get_total_cluster_memory_usage(self):
        """Gets the total memory usage of all student pods"""
        total_mem_usage = 0
        for pod in self._pods:
            total_mem_usage += get_pod_memory_request(pod)
        return total_mem_usage

    def get_total_cluster_memory_capacity(self):
        """Returns the total memory capacity of all nodes, as student
        pods can be scheduled on any node that meets its Request criteria"""
        total_mem_capacity = 0
        for node in self._nodes:
            if not node.spec.unschedulable:
                total_mem_capacity += get_node_memory_capacity(node)
        return total_mem_capacity

    def _get_critical_node_names(self):
        """Return a list of nodes where critical pods
        are running"""
        result = []
        for pod in self._pods:
            if not check_list_intersection(pod.metadata.labels, self._options.preemptible_labels):
                pod_hostname = get_pod_host_name(pod)
                if pod_hostname not in result:
                    result.append(pod_hostname)
        return result

    def get_pods_number_on_node(self, node):
        """Return the effective number of pods on the node
        TODO: There must be a better way to determine number
        of running pods on node"""
        result = 0
        for pod in self._pods:
            if get_pod_host_name(pod) == node.metadata.name:
                result += 1
        return result

    def get_cluster_name(self):
        """Return the full name of the cluster"""
        return self._context

    def get_num_schedulable(self):
        """Return number of nodes schedulable AND NOT
        IN THE LIST OF CRITICAL NODES"""
        result = 0
        for node in self._noncritical_nodes:
            if not node.spec.unschedulable:
                result += 1
        return result

    def get_num_unschedulable(self):
        """Return number of nodes unschedulable

        ASSUMING CRITICAL NODES ARE SCHEDULABLE"""
        result = 0
        for node in self._nodes:
            if node.spec.unschedulable:
                result += 1
        return result

    def get_nodes(self):
        return self._nodes

    def get_image_urls(self):
        return self._image_urls

    def get_critical_node_names(self):
        return self._critical_node_names

    def is_test(self):
        return self._test

    def get_min_utilization(self):
        return self._options.min_utilization

    def get_max_utilization(self):
        return self._options.max_utilization
