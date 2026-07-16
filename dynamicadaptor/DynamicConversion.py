from .Message import RenderMessage
from .Repost import Forward
from loguru import logger


def format_message(message: dict) -> RenderMessage:
    """
    将web返回的动态的item格式化成为render所需的数据类型
    Args:
        message: web动态的item

    Returns: RenderMessage

    """
    header = message["modules"]["module_author"]
    message_id = message["id_str"]
    major = message["modules"]["module_dynamic"]["major"]
    additional = message["modules"]["module_dynamic"]["additional"]
    if message.get("orig") is not None:
        try:
            forward_type = message["orig"]["type"]
            forward_header = message["orig"]["modules"]["module_author"]
            try:
                forward_major = message["orig"]["modules"]["module_dynamic"]["major"]
            except Exception:
                forward_major = None
            forward_additional = message["orig"]["modules"]["module_dynamic"]["additional"]
            forward_text = message["orig"]["modules"]["module_dynamic"]["desc"]
            if message["orig"]["modules"]["module_dynamic"]["topic"] is not None:
                if forward_text:
                    forward_text["topic"] = message["orig"]["modules"]["module_dynamic"][
                        "topic"
                    ]
                else:
                    forward_text = {
                        "topic": message["orig"]["modules"]["module_dynamic"]["topic"]
                    }

            forward = Forward(
                header=forward_header,
                message_type=forward_type,
                major=forward_major,
                additional=forward_additional,
                text=forward_text,
            )
        except KeyError:
            forward = None

        except TypeError:
            forward = None
            logger.exception("failed to parse forward")
    else:
        forward = None
    try:
        text = message["modules"]["module_dynamic"]["desc"]
        if text is not None:
            text["topic"] = message["modules"]["module_dynamic"]["topic"]
        else:
            text = {"topic": message["modules"]["module_dynamic"]["topic"]}
    except KeyError:
        text = None

    except TypeError:
        text = None

    except Exception:
        text = None
        logger.exception("failed to parse text")

    render_message = RenderMessage(
        message_type=message["type"],
        message_id=message_id,
        header=header,
        text=text,
        major=major,
        additional=additional,
        forward=forward,
    )

    return render_message


async def formate_message(message: dict) -> RenderMessage:
    """
    向后兼容的异步包装器，保留以兼容旧的外部调用方。

    新代码请直接使用 :func:`format_message`。
    """
    return format_message(message)
