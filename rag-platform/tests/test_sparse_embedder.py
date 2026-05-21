from rag_embeddings.sparse import SparseEmbedder


def test_sparse_embed_non_empty():
    indices, values = SparseEmbedder().embed("исходные данные раздела ТХ")
    assert indices
    assert values
    assert len(indices) == len(values)


def test_sparse_embed_deterministic():
    embedder = SparseEmbedder()
    first = embedder.embed("требуется предусмотреть вентиляцию")
    second = embedder.embed("требуется предусмотреть вентиляцию")
    assert first == second
