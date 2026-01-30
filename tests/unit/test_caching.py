"""
Tests for voice prompt caching functionality
"""
import pytest
import time
import threading
import numpy as np
from app.utils.caching import VoicePromptCache
from tests.utils import generate_test_audio


@pytest.mark.unit
class TestCacheKeyGeneration:
    """Test hash-based cache key generation"""
    
    def test_same_audio_same_key(self):
        """Test same audio generates same key"""
        cache = VoicePromptCache(max_size=10)
        
        audio = generate_test_audio(duration=3.0)
        sample_rate = 24000
        ref_text = "Test text"
        
        # Generate key twice
        key1 = cache._generate_cache_key(audio, sample_rate, ref_text, False)
        key2 = cache._generate_cache_key(audio, sample_rate, ref_text, False)
        
        assert key1 == key2, "Same audio should generate same key"
    
    def test_different_audio_different_key(self):
        """Test different audio generates different key"""
        cache = VoicePromptCache(max_size=10)
        
        audio1 = generate_test_audio(duration=3.0, frequency=440.0)
        audio2 = generate_test_audio(duration=3.0, frequency=550.0)
        sample_rate = 24000
        ref_text = "Test text"
        
        key1 = cache._generate_cache_key(audio1, sample_rate, ref_text, False)
        key2 = cache._generate_cache_key(audio2, sample_rate, ref_text, False)
        
        assert key1 != key2, "Different audio should generate different keys"
    
    def test_different_text_different_key(self):
        """Test different ref_text generates different key"""
        cache = VoicePromptCache(max_size=10)
        
        audio = generate_test_audio(duration=3.0)
        sample_rate = 24000
        
        key1 = cache._generate_cache_key(audio, sample_rate, "Text 1", False)
        key2 = cache._generate_cache_key(audio, sample_rate, "Text 2", False)
        
        assert key1 != key2, "Different text should generate different keys"
    
    def test_different_mode_different_key(self):
        """Test different x_vector_only_mode generates different key"""
        cache = VoicePromptCache(max_size=10)
        
        audio = generate_test_audio(duration=3.0)
        sample_rate = 24000
        ref_text = "Test text"
        
        key1 = cache._generate_cache_key(audio, sample_rate, ref_text, False)
        key2 = cache._generate_cache_key(audio, sample_rate, ref_text, True)
        
        assert key1 != key2, "Different mode should generate different keys"


@pytest.mark.unit
class TestCacheHitMiss:
    """Test cache hit/miss detection"""
    
    def test_cache_miss_on_first_access(self):
        """Test cache miss on first access"""
        cache = VoicePromptCache(max_size=10)
        
        audio = generate_test_audio(duration=3.0)
        sample_rate = 24000
        ref_text = "Test text"
        
        result = cache.get(audio, sample_rate, ref_text, False)
        
        assert result is None, "First access should be cache miss"
        
        stats = cache.get_stats()
        assert stats["misses"] == 1
        assert stats["hits"] == 0
    
    def test_cache_hit_after_put(self):
        """Test cache hit after storing prompt"""
        cache = VoicePromptCache(max_size=10)
        
        audio = generate_test_audio(duration=3.0)
        sample_rate = 24000
        ref_text = "Test text"
        prompt_data = {"prompt": "test_prompt"}
        
        # Store prompt
        cache.put(audio, sample_rate, ref_text, False, prompt_data)
        
        # Retrieve should hit cache
        result = cache.get(audio, sample_rate, ref_text, False)
        
        assert result == prompt_data, "Should retrieve stored prompt"
        
        stats = cache.get_stats()
        assert stats["hits"] == 1
    
    def test_multiple_cache_hits(self):
        """Test multiple cache hits increment counter"""
        cache = VoicePromptCache(max_size=10)
        
        audio = generate_test_audio(duration=3.0)
        sample_rate = 24000
        ref_text = "Test text"
        prompt_data = {"prompt": "test_prompt"}
        
        cache.put(audio, sample_rate, ref_text, False, prompt_data)
        
        # Multiple accesses
        for _ in range(5):
            cache.get(audio, sample_rate, ref_text, False)
        
        stats = cache.get_stats()
        assert stats["hits"] == 5


@pytest.mark.unit
class TestLRUEviction:
    """Test LRU eviction policy"""
    
    def test_eviction_when_full(self):
        """Test oldest entry is evicted when cache is full"""
        cache = VoicePromptCache(max_size=3, ttl_seconds=3600)
        
        # Fill cache
        for i in range(3):
            audio = generate_test_audio(duration=3.0, frequency=440.0 + i * 100)
            cache.put(audio, 24000, f"Text {i}", False, {"prompt": f"prompt_{i}"})
        
        stats = cache.get_stats()
        assert stats["size"] == 3
        assert stats["evictions"] == 0
        
        # Add one more (should evict oldest)
        audio_new = generate_test_audio(duration=3.0, frequency=800.0)
        cache.put(audio_new, 24000, "Text new", False, {"prompt": "prompt_new"})
        
        stats = cache.get_stats()
        assert stats["size"] == 3, "Size should remain at max"
        assert stats["evictions"] == 1, "Should have 1 eviction"
        
        # First item should be gone
        audio_first = generate_test_audio(duration=3.0, frequency=440.0)
        result = cache.get(audio_first, 24000, "Text 0", False)
        assert result is None, "Oldest entry should be evicted"
    
    def test_recently_used_not_evicted(self):
        """Test recently accessed items are not evicted"""
        cache = VoicePromptCache(max_size=3, ttl_seconds=3600)
        
        # Fill cache
        audios = []
        for i in range(3):
            audio = generate_test_audio(duration=3.0, frequency=440.0 + i * 100)
            audios.append(audio)
            cache.put(audio, 24000, f"Text {i}", False, {"prompt": f"prompt_{i}"})
        
        # Access first item (makes it recently used)
        cache.get(audios[0], 24000, "Text 0", False)
        
        # Add new item (should evict item 1, not item 0)
        audio_new = generate_test_audio(duration=3.0, frequency=800.0)
        cache.put(audio_new, 24000, "Text new", False, {"prompt": "prompt_new"})
        
        # First item should still be there
        result = cache.get(audios[0], 24000, "Text 0", False)
        assert result is not None, "Recently used item should not be evicted"
        
        # Second item should be gone
        result = cache.get(audios[1], 24000, "Text 1", False)
        assert result is None, "LRU item should be evicted"


@pytest.mark.unit
class TestTTLExpiration:
    """Test TTL-based expiration"""
    
    def test_expired_entry_not_returned(self):
        """Test expired entries are not returned"""
        cache = VoicePromptCache(max_size=10, ttl_seconds=1)  # 1 second TTL
        
        audio = generate_test_audio(duration=3.0)
        sample_rate = 24000
        ref_text = "Test text"
        
        # Store prompt
        cache.put(audio, sample_rate, ref_text, False, {"prompt": "test_prompt"})
        
        # Should be available immediately
        result = cache.get(audio, sample_rate, ref_text, False)
        assert result is not None
        
        # Wait for expiration
        time.sleep(1.5)
        
        # Should be expired now
        result = cache.get(audio, sample_rate, ref_text, False)
        assert result is None, "Expired entry should not be returned"
    
    def test_expired_entry_removed_from_cache(self):
        """Test expired entries are removed from cache"""
        cache = VoicePromptCache(max_size=10, ttl_seconds=1)
        
        audio = generate_test_audio(duration=3.0)
        cache.put(audio, 24000, "Test", False, {"prompt": "test"})
        
        assert cache.get_stats()["size"] == 1
        
        # Wait for expiration
        time.sleep(1.5)
        
        # Access expired entry
        cache.get(audio, 24000, "Test", False)
        
        # Size should decrease
        assert cache.get_stats()["size"] == 0, "Expired entry should be removed"


@pytest.mark.unit
class TestThreadSafety:
    """Test concurrent cache access"""
    
    def test_concurrent_put_operations(self):
        """Test concurrent put operations are thread-safe"""
        cache = VoicePromptCache(max_size=100, ttl_seconds=3600)
        
        def add_items(start_idx, count):
            for i in range(start_idx, start_idx + count):
                audio = generate_test_audio(duration=3.0, frequency=440.0 + i)
                cache.put(audio, 24000, f"Text {i}", False, {"prompt": f"prompt_{i}"})
        
        # Run multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=add_items, args=(i * 10, 10))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Should have 50 items (or max_size if capped)
        stats = cache.get_stats()
        assert stats["size"] <= 100
    
    def test_concurrent_get_operations(self):
        """Test concurrent get operations are thread-safe"""
        cache = VoicePromptCache(max_size=100, ttl_seconds=3600)
        
        # Pre-fill cache
        audio = generate_test_audio(duration=3.0)
        cache.put(audio, 24000, "Test", False, {"prompt": "test_prompt"})
        
        results = []
        
        def get_item():
            result = cache.get(audio, 24000, "Test", False)
            results.append(result)
        
        # Run multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=get_item)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All should get the same result
        assert len(results) == 10
        assert all(r == {"prompt": "test_prompt"} for r in results)


@pytest.mark.unit
class TestCacheStatistics:
    """Test cache statistics"""
    
    def test_hit_rate_calculation(self):
        """Test hit rate is calculated correctly"""
        cache = VoicePromptCache(max_size=10)
        
        audio = generate_test_audio(duration=3.0)
        
        # 1 miss
        cache.get(audio, 24000, "Test", False)
        
        # Store
        cache.put(audio, 24000, "Test", False, {"prompt": "test"})
        
        # 3 hits
        for _ in range(3):
            cache.get(audio, 24000, "Test", False)
        
        stats = cache.get_stats()
        assert stats["hits"] == 3
        assert stats["misses"] == 1
        assert stats["total_requests"] == 4
        assert stats["hit_rate_percent"] == 75.0  # 3/4 = 75%
    
    def test_stats_reset(self):
        """Test statistics can be reset"""
        cache = VoicePromptCache(max_size=10)
        
        audio = generate_test_audio(duration=3.0)
        cache.put(audio, 24000, "Test", False, {"prompt": "test"})
        cache.get(audio, 24000, "Test", False)
        
        stats = cache.get_stats()
        assert stats["hits"] > 0
        
        # Reset
        cache.reset_stats()
        
        stats = cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["evictions"] == 0


@pytest.mark.unit
class TestCacheClear:
    """Test cache clearing"""
    
    def test_clear_removes_all_entries(self):
        """Test clear removes all cached entries"""
        cache = VoicePromptCache(max_size=10)
        
        # Add multiple entries
        for i in range(5):
            audio = generate_test_audio(duration=3.0, frequency=440.0 + i * 100)
            cache.put(audio, 24000, f"Text {i}", False, {"prompt": f"prompt_{i}"})
        
        assert cache.get_stats()["size"] == 5
        
        # Clear
        cache.clear()
        
        assert cache.get_stats()["size"] == 0, "Cache should be empty after clear"
        
        # All entries should be gone
        for i in range(5):
            audio = generate_test_audio(duration=3.0, frequency=440.0 + i * 100)
            result = cache.get(audio, 24000, f"Text {i}", False)
            assert result is None, "No entries should remain after clear"
