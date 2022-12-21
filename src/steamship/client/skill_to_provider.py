from typing import Any, Dict

from pydantic import BaseModel

from steamship.client.skills import Skill
from steamship.client.vendors import Vendor


class SkillVendorConfig(BaseModel):
    plugin_handle: str
    config: Dict[str, Any]


SKILL_TO_PROVIDER: Dict[Skill, Dict[Vendor, SkillVendorConfig]] = {
    Skill.ENTITIES: {
        Vendor.OneAI: SkillVendorConfig(
            plugin_handle="oneai-tagger",
            config={"skills": ["names", "numbers", "business-entities"]},
        )
    },
    Skill.SUMMARY: {
        Vendor.OneAI: SkillVendorConfig(
            plugin_handle="oneai-tagger", config={"skills": ["summarize"]}
        )
    },
    Skill.SENTIMENTS: {
        Vendor.OneAI: SkillVendorConfig(
            plugin_handle="oneai-tagger", config={"skills": ["sentiments"]}
        )
    },
    Skill.EMOTIONS: {
        Vendor.OneAI: SkillVendorConfig(
            plugin_handle="oneai-tagger", config={"skills": ["emotions"]}
        )
    },
    Skill.TOPICS: {
        Vendor.OneAI: SkillVendorConfig(
            plugin_handle="oneai-tagger", config={"skills": ["article-topics"]}
        ),
    },
    Skill.HIGHLIGHTS: {
        Vendor.OneAI: SkillVendorConfig(
            plugin_handle="oneai-tagger", config={"skills": ["highlights"]}
        )
    },
    Skill.KEYWORDS: {
        Vendor.OneAI: SkillVendorConfig(
            plugin_handle="oneai-tagger", config={"skills": ["keywords"]}
        )
    },
}
