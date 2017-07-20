import logging

from .utils import populate_pods

scale_logger = logging.getLogger("scale")


def populate(k8s):
    # FIXME: Remove all calls to this function after auto-pulling images
    scale_logger.debug("Populate images to new or newly schedulable nodes")
    for image_url in k8s.get_image_urls():
        populate_pods(k8s.get_cluster_name(), image_url)
    scale_logger.debug("Populate finished")
