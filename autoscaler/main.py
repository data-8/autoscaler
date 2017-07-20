#!/usr/bin/python3

import logging
import argparse

from .autoscaler import Autoscaler
from .settings import settings


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


if __name__ == "__main__":
    main()
