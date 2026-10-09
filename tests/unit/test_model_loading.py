"""Tests for cache-first Hugging Face model resolution."""
from unittest.mock import patch

from huggingface_hub.errors import LocalEntryNotFoundError

from app.models.manager import _resolve_model_path


def test_cached_snapshot_is_preferred(tmp_path):
    """A complete cached snapshot avoids passing a Hub ID to the model loader."""
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()

    with patch("app.models.manager.snapshot_download", return_value=str(snapshot)) as download:
        resolved = _resolve_model_path(
            "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice", cache_first=True
        )

    assert resolved == str(snapshot)
    download.assert_called_once_with(
        "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice", local_files_only=True
    )


def test_missing_snapshot_falls_back_to_hub():
    """A model never loaded locally remains downloadable from the Hub."""
    model_id = "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"

    with patch(
        "app.models.manager.snapshot_download",
        side_effect=LocalEntryNotFoundError("not cached"),
    ):
        resolved = _resolve_model_path(model_id, cache_first=True)

    assert resolved == model_id


def test_cache_first_can_be_disabled():
    """Disabling cache-first retains the upstream loading behavior."""
    model_id = "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"

    with patch("app.models.manager.snapshot_download") as download:
        resolved = _resolve_model_path(model_id, cache_first=False)

    assert resolved == model_id
    download.assert_not_called()


def test_explicit_local_model_path_is_preserved(tmp_path):
    """Configured model directories never query the Hugging Face cache."""
    with patch("app.models.manager.snapshot_download") as download:
        resolved = _resolve_model_path(str(tmp_path), cache_first=True)

    assert resolved == str(tmp_path)
    download.assert_not_called()
