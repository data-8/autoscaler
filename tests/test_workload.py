from autoscaler import workload, settings
from .test_kubernetes_control import get_test_k8s
from .testing_utils import check_expected


class TestWorkload(object):

    _k8s = get_test_k8s()

    def test_get_effective_utilization(self):
        check_expected(
            workload.get_effective_utilization,
            [self._k8s],
            float,
            0.16534503348334964
        )

    def test_schedule_goal(self):
        custom_settings = settings.settings()

        check_expected(
            workload.schedule_goal,
            [self._k8s, custom_settings],
            int,
            15
        )

        custom_settings.min_nodes = 1
        check_expected(
            workload.schedule_goal,
            [self._k8s, custom_settings],
            int,
            3
        )

        custom_settings.max_utilization = 0.5
        custom_settings.min_utilization = 0.2
        custom_settings.optimal_utilization = 0.35
        check_expected(
            workload.schedule_goal,
            [self._k8s, custom_settings],
            int,
            7
        )

        custom_settings.min_nodes = 8
        check_expected(
            workload.schedule_goal,
            [self._k8s, custom_settings],
            int,
            8
        )

        custom_settings.max_utilization = 1
        custom_settings.min_utilization = 0.1
        custom_settings.optimal_utilization = 0.16534503348334964
        check_expected(
            workload.schedule_goal,
            [self._k8s, custom_settings],
            int,
            15
        )
