from rag_drawings.extractor import highlight_bboxes_png


def test_highlight_bboxes_png():
    from PIL import Image
    from io import BytesIO

    img = Image.new("RGB", (200, 100), color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    out = highlight_bboxes_png(
        buf.getvalue(),
        [{"bbox": [10, 10, 80, 40], "label": "stamp", "element_type": "stamp"}],
    )
    assert len(out) > 100
