import importlib


def test_package_imports():
    assert importlib.import_module("emva_sim").__name__ == "emva_sim"
