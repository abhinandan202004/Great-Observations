from datetime import UTC, datetime, timedelta

from infrawatch_core.alerting import Comparator, Rule, breaches, firing_since

T0 = datetime(2026, 11, 19, 9, 0, tzinfo=UTC)
STALE = timedelta(seconds=30)
RULE = Rule(Comparator.ABOVE, threshold=15, duration=timedelta(seconds=60))


def series(*values: float, step: int = 5) -> list[tuple[datetime, float]]:
    return [(T0 + timedelta(seconds=i * step), v) for i, v in enumerate(values)]


def end(samples: list[tuple[datetime, float]]) -> datetime:
    return samples[-1][0]


def test_a_breach_lasting_the_duration_fires_from_its_first_sample() -> None:
    samples = series(2, 3, *[40] * 13)  # 13 breaching samples span 60 s

    assert firing_since(RULE, samples, end(samples), STALE) == samples[2][0]


def test_a_breach_shorter_than_the_duration_does_not_fire() -> None:
    samples = series(2, *[40] * 12)  # spans 55 s

    assert firing_since(RULE, samples, end(samples), STALE) is None


def test_one_normal_sample_resets_the_run() -> None:
    samples = series(*[40] * 10, 2, *[40] * 5)

    assert firing_since(RULE, samples, end(samples), STALE) is None


def test_a_transient_spike_on_a_normal_baseline_never_fires() -> None:
    samples = series(*([0, 0, 8, 0, 4, 0] * 20))

    assert firing_since(RULE, samples, end(samples), STALE) is None


def test_stale_data_does_not_fire() -> None:
    samples = series(*[40] * 20)

    assert firing_since(RULE, samples, end(samples) + timedelta(minutes=5), STALE) is None
    assert firing_since(RULE, [], T0, STALE) is None


def test_below_rules_fire_on_low_values_and_the_threshold_itself_is_not_a_breach() -> None:
    low = Rule(Comparator.BELOW, threshold=1, duration=timedelta(0))

    assert breaches(low, 0.5)
    assert not breaches(low, 1)
    assert not breaches(RULE, 15)
