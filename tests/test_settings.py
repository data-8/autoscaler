from autoscaler import settings


class TestSettings:

    def test_settings(self):
        my_settings = settings.settings()

        assert my_settings.max_utilization == 0.85
        assert my_settings.min_utilization == 0.65
        assert my_settings.optimal_utilization == 0.75
        assert my_settings.min_nodes == 15
        assert my_settings.max_nodes == 75
        assert my_settings.zone == "us-central1-a"
        assert my_settings.project == "92948014362"
        assert my_settings.env_delimiter == ":"
        assert my_settings.preemptible_labels == ['']
        assert my_settings.omit_labels == ['']
        assert my_settings.omit_namespaces == ['kube-system']
        assert my_settings.test_cloud is True
        assert my_settings.test_k8s is True
        assert my_settings.yes is False
        assert my_settings.context == ""
        assert my_settings.context_cloud == ""
        assert my_settings.slack_token == ""
        assert my_settings.default_context == "prod"
