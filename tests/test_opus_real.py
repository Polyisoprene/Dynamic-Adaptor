import asyncio
import json
import pathlib

import pytest

from dynamicadaptor import RenderMessage, format_message, formate_message

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "opus_dynamic.json"


@pytest.fixture(scope="module")
def opus_item():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_opus_major_type(opus_item):
    result = format_message(opus_item)
    assert isinstance(result, RenderMessage)
    assert result.major is not None
    assert result.major.type == "MAJOR_TYPE_OPUS"
    assert result.major.opus is not None


def test_opus_fold_action(opus_item):
    result = format_message(opus_item)
    assert result.major.opus.fold_action == ["展开", "收起"]


def test_opus_jump_url(opus_item):
    result = format_message(opus_item)
    assert result.major.opus.jump_url is not None
    assert "bilibili.com/opus" in result.major.opus.jump_url


def test_opus_pics_captured(opus_item):
    result = format_message(opus_item)
    pics = result.major.opus.pics
    assert pics is not None
    assert len(pics) >= 1
    pic = pics[0]
    assert pic.height == 1200
    assert pic.width == 900
    assert pic.url is not None
    assert pic.size is not None
    assert isinstance(pic.size, float)
    assert pic.live_url is None
    assert pic.aigc is None


def test_opus_summary_text(opus_item):
    result = format_message(opus_item)
    summary = result.major.opus.summary
    assert summary is not None
    assert summary.text is not None
    assert "纸嫁衣9罗浮梦" in summary.text
    assert summary.rich_text_nodes is not None
    assert len(summary.rich_text_nodes) >= 1


def test_opus_no_forward(opus_item):
    result = format_message(opus_item)
    assert result.forward is None


def test_opus_header(opus_item):
    result = format_message(opus_item)
    assert result.header.name == "纸嫁衣官方"
    assert result.header.mid == 1871737115


def test_opus_async_matches_sync(opus_item):
    sync_result = format_message(opus_item)
    async_result = asyncio.run(formate_message(opus_item))
    assert sync_result.model_dump() == async_result.model_dump()
