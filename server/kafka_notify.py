import requests
from datetime import datetime
import html2text
from fastapi import Body


def html_to_markdown(
        content: str = Body(...),
        ignore_images: bool = Body(True),
        ignore_links: bool = Body(True),
        ignore_tables: bool = Body(True)
):
    h = html2text.HTML2Text()
    h.ignore_images = ignore_images
    h.ignore_links = ignore_links
    h.ignore_tables = ignore_tables

    return h.handle(content)


def send_message(chat_session_id: int, question_id: int, query: str, answer: str, platform_tag: str, utoken: str, cid: str, entity_id: str):
    KAFKA_CHAT_HOST = "http://172.18.0.168:8081" if "TGY" == platform_tag[:3] else "http://127.0.0.1:8081"

    if utoken is not None and cid is not None and entity_id is not None:
        requests.post(
                    f"{KAFKA_CHAT_HOST}/chat/send",
                    json={
                        "create_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "chat_session_id": chat_session_id,
                        "question_id": question_id,
                        "question": query,
                        "answer": answer,
                        "platform_tag": platform_tag
                    },
                    headers={
                        "token": utoken,
                        "cid": cid,
                        "entity-id": entity_id
                    }
                )
