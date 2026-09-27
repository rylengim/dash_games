import unittest
from unittest.mock import patch

import pandas as pd

import games_market_dash_Andrei_Olziatiev as dashboard


class DashboardTests(unittest.TestCase):
    def setUp(self):
        # Numeric codes are deliberately present: the chart must use categories,
        # not average these arbitrary encodings.
        self.games = pd.DataFrame(
            [
                ["PS2", "Action", 2001, "E", 1, 6.0, 60.0],
                ["PS2", "Action", 2002, "E", 1, 8.0, 80.0],
                ["PS2", "Action", 2003, "T", 2, 7.0, 70.0],
                ["PC", "Action", 2002, "M", 3, 9.0, 90.0],
                ["PS2", "Sports", 2002, "T", 2, 5.0, 50.0],
                ["PS2", "Action", 2008, "M", 3, 4.0, 40.0],
            ],
            columns=[
                "Platform", "Genre", "Year_of_Release", "Rating",
                "Rating_Num", "User_Score", "Critic_Score",
            ],
        )
        self.data_patch = patch.object(dashboard, "data", self.games)
        self.data_patch.start()
        self.addCleanup(self.data_patch.stop)

    def test_esrb_distribution_counts_categories_after_all_filters(self):
        result = dashboard.update_dashboard(["PS2"], ["Action"], [2000, 2005])
        figure = result[3]
        counts = {
            category: count
            for trace in figure.data
            for category, count in zip(trace.x, trace.y)
        }

        self.assertEqual(counts, {"E": 2, "T": 1})
        self.assertEqual(sum(counts.values()), 3)

    def test_other_metrics_and_charts_keep_the_same_filtered_games(self):
        result = dashboard.update_dashboard(["PS2"], ["Action"], [2000, 2005])

        self.assertEqual(result[0].children, "Общее число игр: 3")
        self.assertEqual(result[1].children, "Средняя оценка игроков: 7.00")
        self.assertEqual(result[2].children, "Средняя оценка критиков: 70.00")
        self.assertEqual(sum(len(trace.x) for trace in result[4].data), 3)
        self.assertEqual(sum(sum(trace.y) for trace in result[5].data), 3)

    def test_empty_filter_result_does_not_invent_rating_counts(self):
        result = dashboard.update_dashboard(["Unknown"], [], [2000, 2010])

        self.assertEqual(result[0].children, "Общее число игр: 0")
        self.assertEqual(result[1].children, "Нет данных")
        self.assertEqual(result[2].children, "Нет данных")
        self.assertEqual(sum(len(trace.x) for trace in result[3].data), 0)


if __name__ == "__main__":
    unittest.main()
