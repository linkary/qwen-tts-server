"""
Tests for concurrent voice prompt resolution (app.utils.caching).

Guards the cache stampede that appears once prompt extraction is awaited: with
`get` -> `await extract` -> `put` spanning an await, identical concurrent
requests all miss, all extract, and all but one result is discarded. With a
small MAX_CONCURRENT_INFERENCES the redundant extractions also occupy GPU
permits, making duplicate requests slower than having no cache at all.
"""
import asyncio
import threading

import pytest

import app.utils.caching as caching
from app.utils.caching import VoicePromptCache, get_or_create_voice_prompt
from app.utils.inference import init_inference, reset_inference_state
from tests.utils import generate_test_audio

SAMPLE_RATE = 24000


class FakeBaseModel:
    """Counts prompt extractions and reports peak concurrent extractions."""

    def __init__(self, duration: float = 0.1):
        self.duration = duration
        self.calls = 0
        self.peak_concurrent = 0
        self._active = 0
        self._guard = threading.Lock()

    def create_voice_clone_prompt(self, ref_audio, ref_text, x_vector_only_mode):
        with self._guard:
            self.calls += 1
            self._active += 1
            self.peak_concurrent = max(self.peak_concurrent, self._active)
        # Blocking, like the real extraction: run_inference offloads it.
        threading.Event().wait(self.duration)
        with self._guard:
            self._active -= 1
        return {'ref_text': ref_text, 'x_vector_only_mode': x_vector_only_mode}


@pytest.fixture
def isolated_cache(monkeypatch):
    """Give each test a private cache and a fresh limiter."""
    cache = VoicePromptCache(max_size=100, ttl_seconds=3600)
    monkeypatch.setattr(caching, '_voice_cache', cache)
    monkeypatch.setattr(caching, '_prompt_locks', caching.KeyedLock())
    reset_inference_state()
    init_inference(max_concurrent=4)
    yield cache
    reset_inference_state()


@pytest.mark.unit
class TestVoicePromptCoalescing:
    """Tests for get_or_create_voice_prompt."""

    async def test_identical_concurrent_requests_extract_once(self, isolated_cache):
        """N identical concurrent requests must trigger exactly one extraction."""
        audio, sample_rate = generate_test_audio(duration=1.0), SAMPLE_RATE
        model = FakeBaseModel()

        results = await asyncio.gather(*(
            get_or_create_voice_prompt(model, audio, sample_rate, 'hello', False)
            for _ in range(5)
        ))

        assert model.calls == 1
        assert model.peak_concurrent == 1

        statuses = [status for _, status in results]
        assert statuses.count('miss') == 1
        assert statuses.count('hit') == 4

        # Every caller gets the same object the leader published.
        prompts = [prompt for prompt, _ in results]
        assert all(p is prompts[0] for p in prompts)

    async def test_cache_statistics_are_not_inflated(self, isolated_cache):
        """
        Coalesced requests must record one miss and N-1 hits.

        Counting N misses for N identical requests makes hit_rate_percent report
        the opposite of what the cache actually did.
        """
        audio, sample_rate = generate_test_audio(duration=1.0), SAMPLE_RATE
        model = FakeBaseModel()

        await asyncio.gather(*(
            get_or_create_voice_prompt(model, audio, sample_rate, 'hello', False)
            for _ in range(4)
        ))

        stats = isolated_cache.get_stats()
        assert stats['misses'] == 1
        assert stats['hits'] == 3
        assert stats['size'] == 1

    async def test_distinct_requests_are_not_serialized(self, isolated_cache):
        """Different cache keys must extract concurrently, not queue behind each other."""
        audio, sample_rate = generate_test_audio(duration=1.0), SAMPLE_RATE
        model = FakeBaseModel()

        await asyncio.gather(*(
            get_or_create_voice_prompt(model, audio, sample_rate, f'text-{i}', False)
            for i in range(4)
        ))

        assert model.calls == 4
        assert model.peak_concurrent > 1  # bounded by max_concurrent=4

    async def test_second_wave_is_served_from_cache(self, isolated_cache):
        """Once published, later requests hit the cache without extracting."""
        audio, sample_rate = generate_test_audio(duration=1.0), SAMPLE_RATE
        model = FakeBaseModel()

        _, first = await get_or_create_voice_prompt(
            model, audio, sample_rate, 'hello', False
        )
        _, second = await get_or_create_voice_prompt(
            model, audio, sample_rate, 'hello', False
        )

        assert (first, second) == ('miss', 'hit')
        assert model.calls == 1

    async def test_failed_extraction_does_not_poison_the_key(self, isolated_cache):
        """A failed extraction must leave the key usable and cache nothing."""
        audio, sample_rate = generate_test_audio(duration=1.0), SAMPLE_RATE

        class FailingModel:
            def create_voice_clone_prompt(self, **kwargs):
                raise RuntimeError('extraction failed')

        with pytest.raises(RuntimeError, match='extraction failed'):
            await get_or_create_voice_prompt(
                FailingModel(), audio, sample_rate, 'hello', False
            )

        assert isolated_cache.get_stats()['size'] == 0

        model = FakeBaseModel()
        prompt, status = await get_or_create_voice_prompt(
            model, audio, sample_rate, 'hello', False
        )
        assert status == 'miss'
        assert prompt is not None

    async def test_cache_disabled_bypasses_cache(self, isolated_cache, monkeypatch):
        """With caching off, every request extracts and nothing is stored."""
        from app.config import settings

        monkeypatch.setattr(settings, 'voice_cache_enabled', False)
        audio, sample_rate = generate_test_audio(duration=1.0), SAMPLE_RATE
        model = FakeBaseModel()

        results = await asyncio.gather(*(
            get_or_create_voice_prompt(model, audio, sample_rate, 'hello', False)
            for _ in range(3)
        ))

        assert model.calls == 3
        assert [status for _, status in results] == ['disabled'] * 3
        assert isolated_cache.get_stats()['size'] == 0
