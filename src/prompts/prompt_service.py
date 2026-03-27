from functools import lru_cache


class PromptService:

    def __init__(self, repository):
        self.repository = repository

    @lru_cache
    def _get_prompt(self, key: str):
        return self.repository.get_by_key(key)

    def get_prompt(self, key: str, **kwargs):
        prompt = self._get_prompt(key)
        content = prompt.content
        if kwargs:
            content = content.format(**kwargs)
        return content
