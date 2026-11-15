import io
import wave
from pathlib import Path
from types import SimpleNamespace

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest


def upload_wav(duration, file_id="first"):
    data = io.BytesIO()
    with wave.open(data, "wb") as audio:
        audio.setparams((1, 2, 8000, 0, "NONE", "not compressed"))
        audio.writeframes(b"\x00\x00" * round(8000 * duration))
    return SimpleNamespace(name="sample.wav", file_id=file_id, getvalue=data.getvalue)


@pytest.fixture
def app(monkeypatch):
    uploader = SimpleNamespace(file=None)
    monkeypatch.setattr(st, "file_uploader", lambda *args, **kwargs: uploader.file)
    return AppTest.from_file(str(Path(__file__).resolve().parents[1] / "streamlit_app.py")), uploader


@pytest.mark.parametrize(
    ("duration", "end", "adjustable"),
    [(0.75, 0.75, False), (28, 28, False), (30, 30, False), (30.9, 30, False), (31, 30, True)],
)
def test_locked_trim_boundaries(app, duration, end, adjustable):
    page, uploader = app
    uploader.file = upload_wav(duration)
    page.run()

    assert not page.exception
    assert bool(page.slider) == adjustable
    assert page.session_state.start_seconds == 0
    assert page.session_state.end_seconds == end

    if adjustable:
        page.slider[0].set_value(1).run()
        assert page.session_state.start_seconds == 1
        assert page.session_state.end_seconds == 31


def test_switch_range_and_replace_same_name_upload(app):
    page, uploader = app
    uploader.file = upload_wav(31)
    page.run()
    page.checkbox[1].uncheck().run()
    page.slider[0].set_value((4.0, 4.0)).run()
    assert "終點拖到起點之後" in page.warning[0].value
    assert not page.button
    page.slider[0].set_value((4.0, 8.0)).run()
    assert (page.session_state.start_seconds, page.session_state.end_seconds) == (4, 8)
    page.button[0].click().run()
    assert len(page.get("audio")) == 2

    page.slider[0].set_value((5.0, 9.0)).run()
    assert len(page.get("audio")) == 1

    uploader.file = upload_wav(28, file_id="second")
    page.run()
    assert not page.exception
    assert page.slider[0].value == (0, 28)
    page.checkbox[1].check().run()
    assert not page.exception
    assert not page.slider
    assert (page.session_state.start_seconds, page.session_state.end_seconds) == (0, 28)


def test_invalid_upload_offers_recovery(app):
    page, uploader = app
    uploader.file = SimpleNamespace(name="invalid.wav", file_id="invalid", getvalue=lambda: b"invalid")
    page.run()
    assert not page.exception
    assert "請重新選擇" in page.error[0].value
    assert not page.button

    uploader.file = upload_wav(28)
    page.run()
    assert not page.exception
    assert not page.error
    assert len(page.button) == 2
