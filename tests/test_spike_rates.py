import csv
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import numpy as np
from scipy.io import savemat

SCRIPT = Path(__file__).resolve().parents[1] / 'Analysis-of-Orientation-Tuning-in-V1-Neurons' / 'analyze_v1_tuning.py'
spec = importlib.util.spec_from_file_location('tuning', SCRIPT)
tuning = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tuning)


class RateChecks(unittest.TestCase):
    def fixture(self, conditions=11, trials=2):
        events = np.empty((1, conditions, trials), dtype=object)
        for i in np.ndindex(events.shape):
            events[i] = np.array([0.1, 0.28, 0.5, 1.0, 1.28, 1.5])
        return events

    def test_known_counts_and_matlab_roundtrip(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'fixture.mat'
            savemat(path, {'data': {'EVENTS': self.fixture()}})
            loaded = tuning.load_events(path)
            rates, means, sems = tuning.calculate_rates(loaded)
            self.assertEqual(rates.shape, (1, 11, 2))
            np.testing.assert_allclose(means, 4)
            np.testing.assert_allclose(sems, 0)

    def test_empty_spikes_and_one_trial(self):
        events = self.fixture(trials=1)
        events[0, 0, 0] = np.array([])
        _, mean, sem = tuning.calculate_rates(events)
        self.assertEqual(mean[0, 0], 0)
        self.assertTrue(np.isnan(sem).all())

    def test_corrupt_times_and_window(self):
        events = self.fixture()
        events[0, 0, 0] = np.array([np.nan])
        with self.assertRaises(ValueError):
            tuning.calculate_rates(events)
        with self.assertRaises(ValueError):
            tuning.calculate_rates(self.fixture(), 1, 1)

    def test_explicit_angle_mapping(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'angles.csv'
            path.write_text('condition_index,angle_degrees\n1,90\n0,0\n')
            np.testing.assert_array_equal(tuning.load_angles(path, 2, 'orientation'), [0, 90])
            with self.assertRaises(ValueError):
                tuning.load_angles(path, 11, 'orientation')
            path.write_text('condition_index,angle_degrees\n0,0\n0,90\n')
            with self.assertRaises(ValueError):
                tuning.load_angles(path, 2, 'orientation')

    def test_missing_file_returns_error(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run([sys.executable, str(SCRIPT), '--input', str(Path(temp)/'missing.mat')],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)

    def test_demo_cli_and_output_labels(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run([sys.executable, str(SCRIPT), '--demo', '--output', temp],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((Path(temp) / 'neuron_0_condition_response.png').is_file())
            with (Path(temp) / 'firing_rates.csv').open() as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 12)
            self.assertTrue(all(r['source'] == 'synthetic demonstration' for r in rows))
            self.assertTrue(all(r['angle_degrees'] == '' for r in rows))


if __name__ == '__main__':
    unittest.main()
