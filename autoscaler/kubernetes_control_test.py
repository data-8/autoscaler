#!/usr/bin/python3

"""Provides read and write access to Kubernetes API"""

from kubernetes import client
import logging

from .kubernetes_control import k8s_control

scale_logger = logging.getLogger("scale")
logging.getLogger("kubernetes").setLevel(logging.WARNING)


class k8s_control_test(k8s_control):

    """Dummy test class for k8s_control"""
    _test = True

    def __init__(self, options):
        k8s_control.__init__(self, options)

    def set_unschedulable(self, node_name, value=True):
        """Set the spec key 'unschedulable'"""
        scale_logger.debug(
            "Setting %s node's unschedulable property to %r", node_name, value)
        assert node_name not in self.critical_node_names
        client.V1Node(
            api_version="v1",
            kind="Node",
            metadata=client.V1ObjectMeta(name=node_name),
            spec=client.V1NodeSpec(unschedulable=value)
        )
