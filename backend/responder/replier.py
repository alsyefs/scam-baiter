import os.path
import random
import re
from abc import ABC, abstractmethod
from text_utils.text_filter import *
from .Chatgpt_Replier import gen_text1, gen_text2
from .classifier import classify
from globals import MAIL_ARCHIVE_DIR, TEMPLATES_DIR
from logs import LogManager
log = LogManager.get_logger()

text_filters = [
    RemoveSymbolLineTextFilter(),
    RemoveInfoLineTextFilter(),
    RemoveSensitiveInfoTextFilter(),
    RemoveSpecialPunctuationTextFilter(),
    RemoveStrangeWord(),
    MultiSymbolIntegrationTextFilter(),
]

class Replier(ABC):
    name = "AbstractReplier"

    @abstractmethod
    def _gen_text(self, prompt) -> str:
        log.info(f"Generating reply using {self.name}")
        return prompt

    def get_reply(self, content):
        try:
            for text_filter in text_filters:
                content = text_filter.filter(content)
            res = self._gen_text(content)
            if "[bait_end]" in res:
                res = res.split("[bait_end]", 1)[0]
            m = re.match(r"^.*[.?!]", res, re.DOTALL)
            if m:
                res = m.group(0)
            return res
        except Exception as e:
            log.error(f"Error in get_reply: {e}")
            return ""

    def get_reply_by_his(self, addr):
        try:
            with open(os.path.join(MAIL_ARCHIVE_DIR, addr + ".his"), "r", encoding="utf8") as f:
                content = f.read()
            return self.get_reply(content + "\n[bait_start]\n")
        except Exception as e:
            log.error(f"Error in get_reply_by_his: {e}")
            return ""

class TemplateReplier(Replier):
    name = "Template"
    def _gen_text(self, prompt) -> str:
        try:
            template_dir = os.path.join(TEMPLATES_DIR, random.choice(os.listdir(TEMPLATES_DIR)))
            target_filename = random.choice(os.listdir(template_dir))
            with open(os.path.join(template_dir, target_filename), "r", encoding="utf8") as f:
                res = f.read()
            return res + "[bait_end]"
        except Exception as e:
            log.error(f"Error in TemplateReplier _gen_text: {e}")
            return ""

class ChatReplier1(Replier):
    name = "Chat1"
    def _gen_text(self,prompt) -> str:
        try:
            log.info(f"Generating reply using {self.name}")
            log.info(f"Prompt: {prompt}")
            res = gen_text1(prompt)
            log.info(f"Reply: {res}")
            return res + "[bait_end]"
        except Exception as e:
            log.error(f"Error in ChatReplier1 _gen_text: {e}")
            return ""

class ChatReplier2(Replier):
    name = "Chat2"
    def _gen_text(self,prompt) -> str:
        try:
            log.info(f"Generating reply using {self.name}")
            log.info(f"Prompt: {prompt}")
            res = gen_text2(prompt)
            log.info(f"Reply: {res}")
            return res + "[bait_end]"
        except Exception as e:
            log.error(f"Error in ChatReplier2 _gen_text: {e}")
            return ""
