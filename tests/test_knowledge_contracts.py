from src.knowledge.intake import KnowledgeDraft, KnowledgeIntakeValidator


def test_knowledge_item_always_has_provenance_hash() -> None:
    item = KnowledgeIntakeValidator().create_item(
        item_id="item-1",
        source_id="source-1",
        draft=KnowledgeDraft(
            source_type="local_document",
            locator="docs/example.md",
            title="Example",
            content="Paris is the capital of France.",
            language="en",
            confidence=1.0,
        ),
    )
    assert len(item.source.content_sha256) == 64
    assert item.source.locator == "docs/example.md"
