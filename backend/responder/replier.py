import os.path
import random
import re
from abc import ABC, abstractmethod
from text_utils.text_filter import *
from .Chatgpt_Replier import gen_text_1, gen_text_2, gen_text_3, gen_text_4, gen_text_5, gen_text_6
from globals import MAIL_ARCHIVE_DIR
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
    def _gen_text(self, prompt, old_summary_context="") -> str:
        log.info(f"Generating reply using {self.name}")
        return prompt

    def get_reply(self, content, old_summary_context=""):
        try:
            for text_filter in text_filters:
                content = text_filter.filter(content)
            generated_response, new_summary_context = self._gen_text(content, old_summary_context)
            if "[bait_end]" in generated_response:
                generated_response = generated_response.split("[bait_end]", 1)[0]
            m = re.match(r"^.*[.?!]", generated_response, re.DOTALL)
            if m:
                generated_response = m.group(0)
            return generated_response, new_summary_context
        except Exception as e:
            log.error(f"Error in get_reply: {e}")
            return ""

    # def get_reply_by_his(self, addr):
    #     try:
    #         with open(os.path.join(MAIL_ARCHIVE_DIR, addr + ".his"), "r", encoding="utf8") as f:
    #             content = f.read()
    #         return self.get_reply(content + "\n[bait_start]\n")
    #     except Exception as e:
    #         log.error(f"Error in get_reply_by_his: {e}")
    #         return ""

class ChatReplier1(Replier):
    name = "Chat1"
    def _gen_text(self,prompt, old_summary_context="") -> str:
        try:
            generated_response, new_summary_context = gen_text_1(prompt, old_summary_context)
            return generated_response + "[bait_end]", new_summary_context
        except Exception as e:
            log.error(f"Error in ChatReplier1 _gen_text: {e}")
            return ""

class ChatReplier2(Replier):
    name = "Chat2"
    def _gen_text(self,prompt, old_summary_context="") -> str:
        try:
            generated_response, new_summary_context = gen_text_2(prompt, old_summary_context)
            return generated_response + "[bait_end]", new_summary_context
        except Exception as e:
            log.error(f"Error in ChatReplier2 _gen_text: {e}")
            return ""

class ChatReplier3(Replier):
    name = "Chat3"
    def _gen_text(self,prompt, old_summary_context="") -> str:
        try:
            generated_response, new_summary_context = gen_text_3(prompt, old_summary_context)
            return generated_response + "[bait_end]", new_summary_context
        except Exception as e:
            log.error(f"Error in ChatReplier3 _gen_text: {e}")
            return ""
class ChatReplier4(Replier):
    name = "Chat4"
    def _gen_text(self,prompt, old_summary_context="") -> str:
        try:
            generated_response, summary_context = gen_text_4(prompt, old_summary_context)
            return generated_response + "[bait_end]", summary_context
        except Exception as e:
            log.error(f"Error in ChatReplier4 _gen_text: {e}")
            return ""
        
class ChatReplier5(Replier):
    name = "Chat5"
    def _gen_text(self,prompt, old_summary_context="") -> str:
        try:
            generated_response, new_summary_context = gen_text_5(prompt, old_summary_context)
            return generated_response + "[bait_end]", new_summary_context
        except Exception as e:
            log.error(f"Error in ChatReplier5 _gen_text: {e}")
            return ""

class ChatReplier6(Replier):
    name = "Chat6"
    def _gen_text(self,prompt, old_summary_context="") -> str:
        try:
            generated_response, new_summary_context = gen_text_6(prompt, old_summary_context)
            return generated_response + "[bait_end]", new_summary_context
        except Exception as e:
            log.error(f"Error in ChatReplier6 _gen_text: {e}")
            return ""