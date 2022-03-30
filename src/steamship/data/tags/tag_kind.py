class TagKind:
    """This class provides a set of `kind` constants for Tags"""
    pos = "pos"  # Part of speech tags
    dep = "dep"  # Dependency tags
    ent = "ent"  # Entity tags, such as PERSON or ORG
    doc = "doc"  # Doc-level semantics, such as H1, P, S
    text = "text"  # Text-level semantics, such as whether the span is a phone number
