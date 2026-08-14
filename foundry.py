"""
foundry.py - Singleton Foundry Local manager.

FoundryLocalManager is a process-level singleton. This module provides
a single get_manager() entry point so both ingest.py and rag.py share
the same initialized instance without re-initializing.

Usage:
    from foundry import get_manager
    manager = get_manager()
    model = manager.catalog.get_model("some-alias")
"""

from foundry_local_sdk import FoundryLocalManager, Configuration

_initialized = False


def get_manager() -> FoundryLocalManager:
    """Return the singleton FoundryLocalManager, initializing it on first call."""
    global _initialized
    if not _initialized:
        config = Configuration(app_name="rag-assistant")
        FoundryLocalManager.initialize(config)
        _initialized = True
    return FoundryLocalManager.instance


def ensure_model(alias: str, verbose: bool = True):
    """
    Ensure a model is downloaded and loaded. Returns the IModel object.

    Downloads if not in local cache. Loads if not currently in memory.
    """
    manager = get_manager()
    model = manager.catalog.get_model(alias)

    if model is None:
        raise RuntimeError(
            f"Model alias '{alias}' not found in the Foundry Local catalog. "
            "Check the alias or run 'foundry model list' in the CLI."
        )

    if not model.is_cached:
        if verbose:
            print(f"[foundry] Downloading '{alias}'... (first run only)")
        model.download()

    if not model.is_loaded:
        if verbose:
            print(f"[foundry] Loading '{alias}' into memory...")
        model.load()

    return model
