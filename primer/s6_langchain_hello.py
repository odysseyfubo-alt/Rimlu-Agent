"""换成 LangChain：说一句话。对照 s1_hello.py。"""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
model = ChatOpenAI(
    model=os.environ["CHAT_MODEL"],
    base_url=os.environ["CHAT_BASE_URL"],
    api_key=os.environ["CHAT_API_KEY"],
)

if __name__ == "__main__":
    reply = model.invoke("到手不喜欢能退吗？")
    print(reply.content)
    print(reply.usage_metadata)
