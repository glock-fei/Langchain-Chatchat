import requests
from datetime import datetime

KAFKA_CHAT_HOST = "http://127.0.0.1:8080"


def send_message(chat_session_id: int, question_id: int, query: str, answer: str, platform_tag: str, utoken: str, cid: str, entity_id: str):
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
