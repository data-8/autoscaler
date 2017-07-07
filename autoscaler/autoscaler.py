import logging
import random
import time
import heapq

from .workload import schedule_goal
from .cluster_update import gce_cluster_control
from .utils import user_confirm as confirm
from .kubernetes_control import k8s_control
from .kubernetes_control_test import k8s_control_test
from .slack_message import slack_handler
from .populate import populate


scale_logger = logging.getLogger("scale")
slack_logger = logging.getLogger("slack")  # used for slack message only


class Autoscaler:
    def __init__(self, options):
        self._options = options
        self._cluster = gce_cluster_control(options)

        if options.test_k8s:
            self._k8s = k8s_control_test(options)
        else:
            self._k8s = k8s_control(options)

        # goal is the total number of nodes we want in the cluster
        self._non_critical_nodes = []

        self._add_slack_handler()

    def scale(self):
        """Update the nodes property based on scaling policy
        and create new nodes if necessary"""

        scale_logger.info("Scaling on cluster %s", self._k8s.get_cluster_name())

        self._goal = schedule_goal(self._k8s, self._options)
        self._update_non_critical_node_list()

        scale_logger.info("Total nodes in the cluster: %i", len(self._k8s.get_nodes()))
        scale_logger.info(
            "%i nodes are unschedulable at this time", self._k8s.get_num_unschedulable())
        scale_logger.info("Found %i critical nodes",
                          len(self._k8s.get_nodes()) - len(self._non_critical_nodes))
        scale_logger.info("Recommending total %i nodes for service", self._goal)

        if confirm(("Updating unschedulable flags to ensure %i nodes are unschedulable" % max(len(self._k8s.get_nodes()) - self._goal, 0))):
            self._update_unschedulable()

        if self._goal > len(self._k8s.get_nodes()):
            scale_logger.info(
                "Resize the cluster to %i nodes to satisfy the demand", self._goal)
            if self._options.test_cloud:
                self._resize_for_new_nodes_test()
            else:
                slack_logger.info(
                    "Cluster resized to %i nodes to satisfy the demand", self._goal)
                self._resize_for_new_nodes()
        if self._options.test_cloud:
            self._shutdown_empty_nodes_test()
        else:
            # CRITICAL NODES SHOULD NOT BE SHUTDOWN
            self._shutdown_empty_nodes()

    def _update_non_critical_node_list(self):
        # a list of nodes that are NOT critical
        self._non_critical_nodes = self._get_non_critical_nodes()

        # Shuffle the node list so that when there are multiple nodes
        # with same number of pods, they will be randomly picked to
        # be made unschedulable
        random.shuffle(self._non_critical_nodes)

    def _get_non_critical_nodes(self):
        nodes = []
        for node in self._k8s.get_nodes():
            if node.metadata.name not in self._k8s.get_critical_node_names():
                nodes.append(node)
        return nodes

    def _shutdown_empty_nodes(self, test=False):
        """
        Search through all nodes and shut down those that are unschedulable
        and devoid of non-critical pods

        CRITICAL NODES SHOULD NEVER BE INCLUDED IN THE INPUT LIST
        """
        count = 0
        for node in self._non_critical_nodes:
            if self._k8s.get_pods_number_on_node(node) == 0 and node.spec.unschedulable:
                if confirm(("Shutting down empty node: %s" % node.metadata.name)):
                    scale_logger.info(
                        "Shutting down empty node: %s", node.metadata.name)
                    if not test:
                        count += 1
                        self._cluster.shutdown_specified_node(node.metadata.name)
        if count > 0:
            scale_logger.info("Shut down %d empty nodes", count)
            slack_logger.info("Shut down %d empty nodes", count)

    def _shutdown_empty_nodes_test(self):
        self._shutdown_empty_nodes(True)

    def _resize_for_new_nodes(self, test=False, wait_time=None):
        """create new nodes to match self._goal required
        only for scaling up"""
        if confirm(("Resizing up to: %d nodes" % self._goal)):
            scale_logger.info("Resizing up to: %d nodes", self._goal)
            if not test:
                self._cluster.add_new_node(self._goal)
                if not wait_time and wait_time != 0:
                    wait_time = 130
                scale_logger.debug(
                    "Sleeping for %i seconds for the node to be ready for populating", wait_time)
                time.sleep(wait_time)
                populate(self._k8s)

    def _resize_for_new_nodes_test(self):
        self._resize_for_new_nodes(True)

    def _add_slack_handler(self):
        slack_logger.addHandler(slack_handler(self._options.slack_token))
        if not self._options.slack_token:
            scale_logger.info(
                "No message will be sent to slack, since there is no token provided")

    def _update_nodes(self, nodes, is_unschedulable):
        """Update given list of nodes with given
        unschedulable property"""

        updated = []
        for node in nodes:
            self._k8s.set_unschedulable(node.metadata.name, is_unschedulable)
            updated.append(node.metadata.name)
        return updated

    def _update_unschedulable(self, calculate_priority=None):
        """Attempt to make sure given number of
        nodes are blocked, if possible;
        return number of nodes newly blocked; negative
        value means the number of nodes unblocked

        calculate_priority should be a function
        that takes a node and return its priority value
        for being blocked; smallest == highest
        priority; default implementation uses get_pods_number_on_node

        CRITICAL NODES SHOULD NOT BE INCLUDED IN THE INPUT LIST"""

        number_unschedulable = max(len(self._k8s.get_nodes()) - self._goal, 0)
        assert number_unschedulable >= 0
        number_unschedulable = int(number_unschedulable)

        scale_logger.info(
            "Updating unschedulable flags to ensure %i nodes are unschedulable", number_unschedulable)

        if calculate_priority is None:
            # Default implementation based on get_pods_number_on_node
            def calculate_priority(node): return self._k8s.get_pods_number_on_node(node)

        schedulable_nodes = []
        unschedulable_nodes = []

        priority = []

        # Analyze nodes status and establish blocking priority
        for count in range(len(self._non_critical_nodes)):
            if self._non_critical_nodes[count].spec.unschedulable:
                unschedulable_nodes.append(self._non_critical_nodes[count])
            else:
                schedulable_nodes.append(self._non_critical_nodes[count])
            priority.append(
                (calculate_priority(self._non_critical_nodes[count]), count))

        # Attempt to modify property based on priority
        toBlock = []
        toUnBlock = []

        heapq.heapify(priority)
        for _ in range(number_unschedulable):
            if len(priority) > 0:
                _, index = heapq.heappop(priority)
                if self._non_critical_nodes[index] in schedulable_nodes:
                    toBlock.append(self._non_critical_nodes[index])
            else:
                break
        for _, index in priority:
            if self._non_critical_nodes[index] in unschedulable_nodes:
                toUnBlock.append(self._non_critical_nodes[index])

        self._update_nodes(toBlock, True)
        scale_logger.debug("%i nodes newly blocked", len(toBlock))
        self._update_nodes(toUnBlock, False)
        scale_logger.debug("%i nodes newly unblocked", len(toUnBlock))
        if (len(toBlock) != 0 or len(toUnBlock) != 0) and (len(toBlock) != len(toUnBlock)) and not self._k8s.is_test():
            slack_logger.info(
                "%i nodes newly blocked, %i nodes newly unblocked", len(toBlock), len(toUnBlock))
        if len(toUnBlock) != 0:
            populate(self._k8s)

        return len(toBlock) - len(toUnBlock)
