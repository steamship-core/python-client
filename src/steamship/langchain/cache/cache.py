import hashlib
import logging
from typing import Optional

from langchain.cache import RETURN_VAL_TYPE, BaseCache
from langchain.schema import Generation
from pydantic import BaseModel

from steamship import Block, File, Steamship, SteamshipError
from steamship.data import Tag, TagKind


class SteamshipCache(BaseCache, BaseModel):
    """Provide basic Steamship-compatible caching for LangChain LLM calls."""

    client: Steamship

    @staticmethod
    def _handle_for(llm_string) -> str:
        """Generate hash-based ID for a langchain LLM."""
        return f"cache-{hashlib.sha256(llm_string.encode('utf-8')).hexdigest()}"

    def lookup(self, prompt: str, llm_string: str) -> Optional[RETURN_VAL_TYPE]:
        """Look up based on prompt and llm_string.

        LangChain uses the `llm_string` to uniquely identify an LLM instance. This cache uses that to generate
        a unique ID for cache storage within a Steamship workspace.
        """
        cache_handle = SteamshipCache._handle_for(llm_string)
        logging.debug(f"cache lookup: {prompt} in {cache_handle}")
        try:
            cache_file = File.get(self.client, handle=cache_handle)
        except SteamshipError:
            logging.warning(f"no cache found in workspace with handle: {cache_handle}")
            return None

        try:
            # find the Steamship Tag in the cache for the prompt and return the values
            for file_tag in cache_file.tags:
                if file_tag.kind == TagKind.LLM_CACHE and file_tag.name == prompt:
                    value = file_tag.value
                    generations = []
                    for _, text in value.items():
                        generations.append(Generation(text))
                    return generations

            logging.debug(f"cache miss for {prompt}")
            return None
        except SteamshipError as e:
            logging.error(f"cache lookup failure for {prompt}: {e}")
            return None

    def update(self, prompt: str, llm_string: str, return_val: RETURN_VAL_TYPE) -> None:
        """Update cache based on prompt and llm_string.

        LangChain uses the `llm_string` to uniquely identify an LLM instance. This cache uses that to generate
        a unique ID for cache storage within a Steamship workspace.
        """

        cache_handle = SteamshipCache._handle_for(llm_string)
        logging.debug(f"cache update for {prompt} in {cache_handle}")

        try:
            cache_file = File.get(self.client, handle=cache_handle)
        except SteamshipError:
            logging.info(f"no existing cache found for {cache_handle}")
            cache_file = None

        try:
            if cache_file is None:
                # create an empty file to act as our cache
                cache_file = File.create(self.client, blocks=[Block(text="")], handle=cache_handle)

            # delete any existing entry for this prompt first
            for file_tag in cache_file.tags:
                if file_tag.kind == TagKind.LLM_CACHE and file_tag.name == prompt:
                    file_tag.delete()

            value = {}
            for i, generation in enumerate(return_val):
                value[f"generation-{i}"] = generation.text

            # store new value
            Tag.create(
                self.client, file_id=cache_file.id, kind=TagKind.LLM_CACHE, name=prompt, value=value
            )
            return
        except SteamshipError as e:
            logging.warning(f"cache update failure for {prompt} in {cache_handle}: {e}")
            return None
