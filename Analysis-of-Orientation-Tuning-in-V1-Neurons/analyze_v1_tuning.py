"""Trial-averaged spike rates by condition; angles require supplied metadata."""
import argparse
import csv
from pathlib import Path
import sys
import numpy as np
from scipy.io import loadmat


def validate_events(events):
    if not isinstance(events, np.ndarray) or events.ndim != 3 or min(events.shape) < 1:
        raise ValueError("EVENTS needs nonempty axes: units, conditions, trials")
    if events.dtype != object:
        raise ValueError("EVENTS must be a MATLAB cell array of spike-time vectors")
    for index in np.ndindex(events.shape):
        try:
            times = np.asarray(events[index], dtype=float).reshape(-1)
        except (TypeError, ValueError) as error:
            raise ValueError(f"Non-numeric spike times at {index}") from error
        if not np.isfinite(times).all() or np.any(times < 0):
            raise ValueError(f"Spike times must be finite, nonnegative seconds at {index}")


def load_events(path):
    """Read scalar data struct and EVENTS[unit,condition,trial]."""
    data = loadmat(path)
    if "data" not in data or data["data"].size != 1:
        raise ValueError("Expected a scalar MATLAB struct named 'data'")
    record = data["data"].reshape(-1)[0]
    if not record.dtype.names or "EVENTS" not in record.dtype.names:
        raise ValueError("Expected data.EVENTS")
    events = record["EVENTS"]
    validate_events(events)
    return events


def calculate_rates(events, start=0.28, end=1.28):
    """Count in inclusive [start,end], divide by duration in seconds."""
    validate_events(events)
    if not np.isfinite([start, end]).all() or start < 0 or end <= start:
        raise ValueError("Require finite 0 <= window start < end")
    rates = np.empty(events.shape, dtype=float)
    for index in np.ndindex(events.shape):
        times = np.asarray(events[index], dtype=float).reshape(-1)
        rates[index] = np.count_nonzero((times >= start) & (times <= end)) / (end - start)
    mean = rates.mean(axis=2)
    sem = (rates.std(axis=2, ddof=1) / np.sqrt(events.shape[2])
           if events.shape[2] > 1 else np.full(mean.shape, np.nan))
    return rates, mean, sem


def load_angles(path, condition_count, kind):
    """CSV maps every zero-based condition_index to angle_degrees."""
    with Path(path).open(newline="") as handle:
        reader = csv.DictReader(handle)
        if not {"condition_index", "angle_degrees"} <= set(reader.fieldnames or []):
            raise ValueError("Angle CSV needs condition_index and angle_degrees columns")
        rows = list(reader)
    mapping = {}
    for row in rows:
        index, angle = int(row["condition_index"]), float(row["angle_degrees"])
        if index in mapping:
            raise ValueError("Duplicate condition_index in angle CSV")
        mapping[index] = angle
    if set(mapping) != set(range(condition_count)):
        raise ValueError("Angle metadata must cover every condition exactly once")
    if kind not in {"orientation", "direction"}:
        raise ValueError("Specify orientation or direction for the angle metadata")
    angles = np.array([mapping[i] for i in range(condition_count)])
    upper = 180 if kind == "orientation" else 360
    if not np.isfinite(angles).all() or np.any(angles < 0) or np.any(angles >= upper):
        raise ValueError(f"{kind} angles must lie in [0,{upper}) degrees")
    return angles


def demo_events():
    """Synthetic numerical fixture, unrelated to the CRCNS animal recordings."""
    rng = np.random.default_rng(42)
    events = np.empty((2, 6, 8), dtype=object)
    for unit, condition, trial in np.ndindex(events.shape):
        count = rng.poisson(2 + 2 * condition + unit)
        events[unit, condition, trial] = np.sort(rng.uniform(0.28, 1.28, count))
    return events


def save_results(events, output, start, end, max_neurons=20, angles=None,
                 angle_kind=None, synthetic=False):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    if max_neurons < 1:
        raise ValueError("max_neurons must be positive")
    rates, means, sems = calculate_rates(events, start, end)
    if angles is not None and len(angles) != events.shape[1]:
        raise ValueError("Angle count must equal condition count")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with (output / "firing_rates.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["unit_index", "condition_index", "angle_degrees", "mean_rate_hz",
                         "sem_across_trials_hz", "trial_count", "source"])
        for unit, condition in np.ndindex(means.shape):
            writer.writerow([unit, condition, "" if angles is None else angles[condition],
                             means[unit, condition], sems[unit, condition], events.shape[2],
                             "synthetic demonstration" if synthetic else "supplied MATLAB file"])
    x = np.arange(events.shape[1]) if angles is None else angles
    order = np.argsort(x, kind="stable")
    for unit in range(min(max_neurons, events.shape[0])):
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.errorbar(x[order], means[unit, order],
                    yerr=None if events.shape[2] == 1 else sems[unit, order],
                    marker="o", capsize=3)
        ax.set_xlabel("Condition index (angle mapping unavailable)" if angles is None
                      else f"Stimulus {angle_kind} (degrees; supplied metadata)")
        ax.set_ylabel("Mean firing rate (spikes/s; bars = SEM across trials)")
        ax.set_title(("SYNTHETIC DEMONSTRATION — " if synthetic else "") + f"Unit {unit}")
        ax.set_ylim(bottom=0)
        ax.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(output / f"neuron_{unit}_condition_response.png", dpi=150)
        plt.close(fig)
    return means


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="Downloaded pvc-11 .mat file")
    source.add_argument("--demo", action="store_true", help="Use explicitly synthetic spike times")
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    parser.add_argument("--start", type=float, default=0.28)
    parser.add_argument("--end", type=float, default=1.28)
    parser.add_argument("--max-neurons", type=int, default=20)
    parser.add_argument("--angles", type=Path, help="Verified condition-to-angle CSV mapping")
    parser.add_argument("--angle-kind", choices=("orientation", "direction"))
    args = parser.parse_args(argv)
    if bool(args.angles) != bool(args.angle_kind):
        parser.error("Use --angles and --angle-kind together")
    try:
        events = demo_events() if args.demo else load_events(args.input)
        angles = None if args.angles is None else load_angles(args.angles, events.shape[1], args.angle_kind)
        means = save_results(events, args.output, args.start, args.end, args.max_neurons,
                             angles, args.angle_kind, args.demo)
    except (OSError, ValueError, TypeError, NotImplementedError) as error:
        parser.error(str(error))
    print(f"Processed {means.shape[0]} units and {means.shape[1]} conditions; output: {args.output}")
    if angles is None:
        print("Conditions have not been assigned orientations or preferred angles.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
