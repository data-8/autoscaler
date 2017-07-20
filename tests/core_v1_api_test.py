from .testing_utils import json_to_object


class CoreV1ApiTest:

    def __init__(self):
        self._nodes = json_to_object("tests/test-data/nodes.json")
        self._all_pods = json_to_object("tests/test-data/pods-all-namespaces.json")
        self.new_nodes = {}

    def list_node(self):
        return self._nodes

    def list_pod_for_all_namespaces(self):
        return self._all_pods

    def patch_node(self, node_name, new_node):
        self.new_nodes[node_name] = new_node
