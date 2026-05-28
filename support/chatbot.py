from support.ai_responses import build_response
from support.faq_engine import find_faq_answer, get_suggestions


class CustomerServiceBot:
    def reply(self, question):
        answer, category = find_faq_answer(question)
        if not answer:
            answer = build_response(question)
            category = 'general'

        return {
            'answer': answer,
            'category': category,
            'suggestions': get_suggestions()
        }
