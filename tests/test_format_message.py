import asyncio
import copy

import pytest

from dynamicadaptor import RenderMessage, format_message, formate_message
from dynamicadaptor.DynamicConversion import format_message as _dc_format_message


def _header():
    return {
        "name": "测试用户",
        "mid": 12345,
        "face": "https://example.com/face.jpg",
        "pub_time": "1小时前",
        "pub_ts": 1700000000,
        "vip": {"status": 1, "type": 1, "avatar_subscript": 0},
        "pendant": {"pid": 1, "image": "https://example.com/p.png", "pendant_name": "挂件"},
        "official_verify": {"type": -1},
    }


def _draw_major():
    return {
        "type": "MAJOR_TYPE_DRAW",
        "draw": {
            "items": [
                {"height": 100, "width": 100, "src": "a.jpg", "url": "https://example.com/a.jpg"}
            ]
        },
    }


def _archive_major():
    return {
        "type": "MAJOR_TYPE_ARCHIVE",
        "archive": {
            "cover": "c.jpg",
            "title": "视频标题",
            "desc": "简介",
            "duration_text": "10:00",
            "badge": {"text": "投稿视频", "color": "#fff", "bg_color": "#fb7299"},
        },
    }


def _additional():
    return {
        "type": "ADDITIONAL_TYPE_RESERVE",
        "reserve": {
            "title": "预约直播",
            "desc1": {"text": "desc1"},
            "desc2": {"text": "desc2"},
        },
    }


def _desc():
    return {
        "text": "hello world",
        "rich_text_nodes": [
            {"type": "RICH_TEXT_NODE_TYPE_TEXT", "text": "hello world", "orig_text": "hello world"}
        ],
    }


def _topic():
    return {"name": "测试话题"}


def make_message(**overrides):
    msg = {
        "type": "DYNAMIC_TYPE_DRAW",
        "id_str": "999",
        "modules": {
            "module_author": _header(),
            "module_dynamic": {
                "major": _draw_major(),
                "additional": _additional(),
                "desc": _desc(),
                "topic": _topic(),
            },
        },
        "orig": None,
    }
    msg.update(overrides)
    return copy.deepcopy(msg)


def make_orig(**overrides):
    orig = {
        "type": "DYNAMIC_TYPE_WORD",
        "modules": {
            "module_author": _header(),
            "module_dynamic": {
                "major": _archive_major(),
                "additional": _additional(),
                "desc": _desc(),
                "topic": _topic(),
            },
        },
    }
    orig.update(overrides)
    return copy.deepcopy(orig)


def test_normal_post():
    msg = make_message()
    result = format_message(msg)
    assert isinstance(result, RenderMessage)
    assert result.message_type == "DYNAMIC_TYPE_DRAW"
    assert result.message_id == "999"
    assert result.header.name == "测试用户"
    assert result.header.mid == 12345
    assert result.major.type == "MAJOR_TYPE_DRAW"
    assert result.additional.type == "ADDITIONAL_TYPE_RESERVE"
    assert result.text is not None
    assert result.text.text == "hello world"
    assert result.text.topic is not None
    assert result.text.topic.name == "测试话题"
    assert result.forward is None


def test_forward_post():
    msg = make_message(orig=make_orig())
    result = format_message(msg)
    assert result.forward is not None
    assert result.forward.message_type == "DYNAMIC_TYPE_WORD"
    assert result.forward.header.name == "测试用户"
    assert result.forward.major is not None
    assert result.forward.major.type == "MAJOR_TYPE_ARCHIVE"
    assert result.forward.text is not None
    assert result.forward.text.topic.name == "测试话题"


def test_missing_orig_key_does_not_raise():
    msg = make_message()
    del msg["orig"]
    result = format_message(msg)
    assert result.forward is None


def test_forward_missing_major():
    orig = make_orig()
    del orig["modules"]["module_dynamic"]["major"]
    msg = make_message(orig=orig)
    result = format_message(msg)
    assert result.forward is not None
    assert result.forward.major is None


def test_desc_none_with_topic():
    msg = make_message()
    msg["modules"]["module_dynamic"]["desc"] = None
    result = format_message(msg)
    assert result.text is not None
    assert result.text.text is None
    assert result.text.topic is not None
    assert result.text.topic.name == "测试话题"


def test_module_dynamic_none_text_falls_back_to_none():
    msg = make_message()
    msg["modules"]["module_dynamic"]["desc"] = None
    msg["modules"]["module_dynamic"]["topic"] = None
    result = format_message(msg)
    # desc None and topic None -> text becomes {"topic": None} -> Text(text=None, topic=None)
    assert result.text is not None
    assert result.text.topic is None


def test_text_keyerror_falls_back_to_none():
    msg = make_message()
    del msg["modules"]["module_dynamic"]["desc"]
    result = format_message(msg)
    assert result.text is None


def test_async_wrapper_matches_sync():
    msg_sync = make_message(orig=make_orig())
    msg_async = make_message(orig=make_orig())
    sync_result = format_message(msg_sync)
    async_result = asyncio.run(formate_message(msg_async))
    assert sync_result.model_dump() == async_result.model_dump()


def test_package_reexports():
    assert _dc_format_message is format_message
    assert callable(formate_message)


def test_async_wrapper_is_coroutine():
    msg = make_message()
    coro = formate_message(msg)
    assert asyncio.iscoroutine(coro)
    asyncio.run(coro)


@pytest.mark.parametrize("major_factory", [_draw_major, _archive_major])
def test_major_types(major_factory):
    msg = make_message()
    msg["modules"]["module_dynamic"]["major"] = major_factory()
    result = format_message(msg)
    assert result.major is not None
