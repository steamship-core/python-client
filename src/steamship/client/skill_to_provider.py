SKILL_TO_PROVIDER = {
    "entities": {
        "oneai": {
            "plugin_handle": "oneai-tagger",
            "config": {"skills": ["names", "numbers", "business-entities"]},
        },
    },
    "summary": {"oneai": {"plugin_handle": "oneai-tagger", "config": {"skills": ["summarize"]}}},
    "sentiments": {
        "oneai": {"plugin_handle": "oneai-tagger", "config": {"skills": ["sentiments"]}}
    },
    "emotions": {"oneai": {"plugin_handle": "oneai-tagger", "config": {"skills": ["emotions"]}}},
    "topics": {
        "oneai": {
            "plugin_handle": "oneai-tagger",
            "config": {"skills": ["article-topics"]},
        },
    },
    "highlights": {
        "oneai": {
            "plugin_handle": "oneai-tagger",
            "config": {"skills": ["highlights"]},
        },
    },
    "keywords": {
        "oneai": {
            "plugin_handle": "oneai-tagger",
            "config": {"skills": ["keywords"]},
        },
    },

}
