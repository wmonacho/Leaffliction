import sys

import pytest

import Distribution


@pytest.fixture
def captured_dataset(monkeypatch):
    """Intercepte create_charts pour récupérer le dataset calculé par main."""
    calls = []
    monkeypatch.setattr(
        Distribution, "create_charts",
        lambda dataset, root: calls.append((dataset, root)))
    return calls


def test_main_counts_images_per_class(dataset_dir, monkeypatch,
                                      captured_dataset):
    root, counts = dataset_dir
    monkeypatch.setattr(sys, "argv", ["Distribution.py", str(root)])
    Distribution.main()
    dataset, _ = captured_dataset[0]
    assert dataset == counts


def test_main_without_args_prints_usage(monkeypatch, capsys,
                                        captured_dataset):
    monkeypatch.setattr(sys, "argv", ["Distribution.py"])
    Distribution.main()
    assert "Usage" in capsys.readouterr().out
    assert captured_dataset == []


def test_create_charts_empty_dataset(capsys):
    Distribution.create_charts({}, "vide")
    assert "Erreur" in capsys.readouterr().out


def test_create_charts_draws_bar_and_pie(monkeypatch):
    import matplotlib.pyplot as plt
    monkeypatch.setattr(plt, "show", lambda: None)
    Distribution.create_charts({"a": 3, "b": 1}, "root")
    fig = plt.gcf()
    assert len(fig.axes) == 2
    plt.close(fig)
