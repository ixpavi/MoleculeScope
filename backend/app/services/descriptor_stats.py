import csv
import os
import numpy as np
from .. import config


class DescriptorStatsService:
    """Lazily loads the real 7,795-molecule training descriptor matrix
    (features/descriptors.csv) to answer 'where does this value sit in the
    training distribution' queries — a percentile rank plus a normalized
    0-1 position for rendering a distribution marker. Real training data,
    not a fabricated/simulated distribution.

    Degrades to null percentiles if the source file is unavailable, rather
    than blocking a prediction that doesn't strictly need it.
    """

    def __init__(self):
        self._columns = None

    def _load(self):
        if self._columns is not None:
            return self._columns

        columns: dict[str, np.ndarray] = {}
        path = config.DESCRIPTOR_STATS_PATH
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                header = next(reader)
                # First column is an unnamed pandas index; skip it.
                names = header[1:]
                raw_rows = [row[1:] for row in reader]
            if raw_rows:
                matrix = np.array(raw_rows, dtype=np.float64)
                for i, name in enumerate(names):
                    columns[name] = np.sort(matrix[:, i])

        self._columns = columns
        return self._columns

    def percentile_for(self, descriptor_name: str, value: float) -> dict | None:
        columns = self._load()
        sorted_values = columns.get(descriptor_name)
        if sorted_values is None or len(sorted_values) == 0:
            return None

        rank = int(np.searchsorted(sorted_values, value, side="right"))
        percentile = round(100.0 * rank / len(sorted_values), 1)

        lo, hi = float(sorted_values[0]), float(sorted_values[-1])
        position = 0.5 if hi == lo else (value - lo) / (hi - lo)
        position = min(max(position, 0.0), 1.0)

        return {"percentile": percentile, "position": position}


descriptor_stats_service = DescriptorStatsService()
