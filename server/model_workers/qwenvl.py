import sys

from fastchat.conversation import Conversation
from typing import List, Literal, Dict

from fastchat import conversation as conv
from server.model_workers.base import *
from server.model_workers.base import ApiEmbeddingsParams

import re


class QwenvlWorker(ApiModelWorker):
    DEFAULT_EMBED_MODEL = "text-embedding-v1"

    def __init__(
        self,
        *,
        version: Literal["qwen-vl-chat-v1"] = "qwen-vl-chat-v1",
        model_names: List[str] = ["qwen-api"],
        controller_addr: str = None,
        worker_addr: str = None,
        **kwargs,
    ):
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        kwargs.setdefault("context_len", 16384)
        super().__init__(**kwargs)
        self.version = version

    def do_chat(self, params: ApiChatParams) -> Dict:
        import dashscope
        params.load_config(self.model_names[0])

        gen = dashscope.MultiModalConversation()
        # 处理文本内容中出现的图片信息 [图片]
        for item in params.messages:
            content = item["content"]

            item["content"] = []
            images = re.findall(r"\[(.*?)\]", content)
            for img in images:
                item["content"].append({"image": img})
                content = content.replace(f"[{img}]", "")

            item["content"].append({"text": content})

        responses = gen.call(
            model=params.version,
            temperature=params.temperature,
            api_key=params.api_key,
            messages=params.messages,
            result_format='message',  # set the result is message format.
            stream=True,
        )

        for resp in responses:
            if resp["status_code"] == 200:
                if choices := resp["output"]["choices"]:
                    yield {
                        "error_code": 0,
                        "text": choices[0]["message"]["content"],
                    }
            else:
                yield {
                    "error_code": resp["status_code"],
                    "text": resp["message"],
                }

    def do_embeddings(self, params: ApiEmbeddingsParams) -> Dict:
        import dashscope
        params.load_config(self.model_names[0])

        result = []
        i = 0
        while i < len(params.texts):
            texts = params.texts[i:i+25]
            resp = dashscope.TextEmbedding.call(
                model=params.embed_model or self.DEFAULT_EMBED_MODEL,
                input=texts, # 最大25行
                api_key=params.api_key,
            )
            if resp["status_code"] != 200:
                return {"code": resp["status_code"], "msg": resp.message}
            else:
                embeddings = [x["embedding"] for x in resp["output"]["embeddings"]]
                result += embeddings
            i += 25
        return {"code": 200, "data": result}

    def get_embeddings(self, params):
        # TODO: 支持embeddings
        print("embedding")
        print(params)

    def make_conv_template(self, conv_template: str = None, model_path: str = None) -> Conversation:
        # TODO: 确认模板是否需要修改
        return conv.Conversation(
            name=self.model_names[0],
            system_message="你是一个聪明、对人类有帮助的人工智能，你可以对人类提出的问题给出有用、详细、礼貌的回答。",
            messages=[],
            roles=["user", "assistant", "system"],
            sep="\n### ",
            stop_str="###",
        )


if __name__ == "__main__":
    import uvicorn
    from server.utils import MakeFastAPIOffline
    from fastchat.serve.model_worker import app

    worker = QwenvlWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:20007",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=20007)
