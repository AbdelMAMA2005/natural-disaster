import unittest

import pandas as pd

from utils.prep import agg_par_dept


class DepartmentAggregationTests(unittest.TestCase):
    def test_department_summary_reports_counts_without_unsupported_rates(self) -> None:
        records = pd.DataFrame(
            {
                "index": [1, 2, 3],
                "departement": ["01", "01", "02"],
                "libelle_departement": ["Ain", "Ain", "Aisne"],
                "code_geographique": ["01001", "01002", "02001"],
                "famille": ["Inondations", "Sécheresse", "Inondations"],
            }
        )

        summary = agg_par_dept(records).set_index("departement")

        self.assertNotIn("pct_communes", summary.columns)
        self.assertNotIn("nb_communes_total", summary.columns)
        self.assertEqual(summary.loc["01", "nb_arretes"], 2)
        self.assertEqual(summary.loc["01", "nb_communes_touchees"], 2)
        self.assertEqual(summary.loc["02", "nb_arretes"], 1)
        self.assertEqual(summary.loc["02", "nb_communes_touchees"], 1)


if __name__ == "__main__":
    unittest.main()
