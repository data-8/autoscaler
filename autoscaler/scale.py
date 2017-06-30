#!/usr/bin/python3

"""Primary scale logic"""

import logging
import argparse
import random
import time

from .workload import schedule_goal
from .update_nodes import update_unschedulable
from .cluster_update import gce_cluster_control
from .settings import settings
from .utils import user_confirm as confirm
from .kubernetes_control import k8s_control
from .kubernetes_control_test import k8s_control_test
from .slack_message import slack_handler
from .populate import populate


logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s')
scale_logger = logging.getLogger("scale")
slack_logger = logging.getLogger("slack")  # used for slack message only


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose",
        help="Show verbose output (debug)",
        action="store_true"
    )
    parser.add_argument(
        "-T",
        "--test",
        help="Run the script in TEST mode, log expected behavior, \
        no real action will be taken",
        action="store_true"
    )
    parser.add_argument(
        "--test-k8s",
        help="Run the script to test kubernetes actions: \
              log expected commands to kubernetes, no real action \
              on node specs",
        action="store_true"
    )
    parser.add_argument(
        "--test-cloud",
        help="Run the script to test cloud actions: \
              log expected commands to the cloud provider, \
              no real action on actual VM pool",
        action="store_true"
    )
    parser.add_argument(
        "-y",
        help="Run the script without user interactive confirmation",
        action="store_true"
    )
    parser.add_argument(
        "-c",
        "--context",
        required=True,
        help="A unique segment in the context name to specify which to \
        use to instantiate Kubernetes"
    )
    parser.add_argument(
        "--context-for-cloud",
        help="An optional different unique segment in the managed pool \
        name to specify which to use to when resizing cloud managed pools",
        default=""
    )
    args = parser.parse_args()
    if args.verbose:
        scale_logger.setLevel(logging.DEBUG)
    else:
        scale_logger.setLevel(logging.INFO)

    slack_logger.setLevel(logging.INFO)

    # Retrieve settings from the environment
    options = settings()

    if args.test:
        scale_logger.warning(
            "Running in test mode, no action will actually be taken")
    else:
        options.test_k8s = False
        options.test_cloud = False
        if args.test_cloud:
            options.test_cloud = True
            scale_logger.warning(
                "Running in test cloud mode, no action on VM pool")
        if args.test_k8s:
            options.test_k8s = True
            scale_logger.warning(
                "Running in test kubernetes mode, no action on node specs")

    if args.y:
        def confirm(x, y=False):
            return True

    options.context = args.context
    if args.context_for_cloud != "":
        options.context_cloud = args.context_for_cloud
    else:
        options.context_cloud = options.context

    try:
        autoscaler = Autoscaler(options)
        autoscaler.scale()
    except KeyboardInterrupt:
        pass


class Autoscaler:
    def __init__(self, options):
        self._options = options
        self._cluster = gce_cluster_control(options)

        if options.test_k8s:
            self._k8s = k8s_control_test(options)
        else:
            self._k8s = k8s_control(options)

        self._add_slack_handler()

    def scale(self):
        """Update the nodes property based on scaling policy
        and create new nodes if necessary"""

        scale_logger.info("Scaling on cluster %s", self._k8s.get_cluster_name())

        nodes = []  # a list of nodes that are NOT critical
        for node in self._k8s.get_nodes():
            if node.metadata.name not in self._k8s.get_critical_node_names():
                nodes.append(node)

        # Shuffle the node list so that when there are multiple nodes
        # with same number of pods, they will be randomly picked to
        # be made unschedulable
        random.shuffle(nodes)

        # goal is the total number of nodes we want in the cluster
        goal = schedule_goal(self._k8s, self._options)

        scale_logger.info("Total nodes in the cluster: %i", len(self._k8s.get_nodes()))
        scale_logger.info(
            "%i nodes are unschedulable at this time", self._k8s.get_num_unschedulable())
        scale_logger.info("Found %i critical nodes",
                          len(self._k8s.get_nodes()) - len(nodes))
        scale_logger.info("Recommending total %i nodes for service", goal)

        if confirm(("Updating unschedulable flags to ensure %i nodes are unschedulable" % max(len(self._k8s.get_nodes()) - goal, 0))):
            update_unschedulable(max(len(self._k8s.get_nodes()) - goal, 0), nodes, self._k8s)

        if goal > len(self._k8s.get_nodes()):
            scale_logger.info(
                "Resize the cluster to %i nodes to satisfy the demand", goal)
            if self._options.test_cloud:
                self._resize_for_new_nodes_test(goal, self._k8s, self._cluster)
            else:
                slack_logger.info(
                    "Cluster resized to %i nodes to satisfy the demand", goal)
                self._resize_for_new_nodes(goal)
        if self._options.test_cloud:
            self._shutdown_empty_nodes_test(nodes)
        else:
            # CRITICAL NODES SHOULD NOT BE SHUTDOWN
            self._shutdown_empty_nodes(nodes)

    def _shutdown_empty_nodes(self, nodes, test=False):
        """
        Search through all nodes and shut down those that are unschedulable
        and devoid of non-critical pods

        CRITICAL NODES SHOULD NEVER BE INCLUDED IN THE INPUT LIST
        """
        count = 0
        for node in nodes:
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

    def _shutdown_empty_nodes_test(self, nodes):
        self._shutdown_empty_nodes(nodes, True)

    def _resize_for_new_nodes(self, new_total_nodes, test=False):
        """create new nodes to match new_total_nodes required
        only for scaling up"""
        if confirm(("Resizing up to: %d nodes" % new_total_nodes)):
            scale_logger.info("Resizing up to: %d nodes", new_total_nodes)
            if not test:
                self._cluster.add_new_node(new_total_nodes)
                wait_time = 130
                scale_logger.debug(
                    "Sleeping for %i seconds for the node to be ready for populating", wait_time)
                time.sleep(wait_time)
                populate(self._k8s)

    def _resize_for_new_nodes_test(self, new_total_nodes):
        self._resize_for_new_nodes(new_total_nodes, True)

    def _add_slack_handler(self):
        slack_logger.addHandler(slack_handler(self._options.slack_token))
        if not self._options.slack_token:
            scale_logger.info(
                "No message will be sent to slack, since there is no token provided")


if __name__ == "__main__":
    main()
