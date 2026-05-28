(function () {
    const launcher = document.querySelector('[data-chatbot-launcher]');
    const panel = document.querySelector('[data-chatbot-panel]');
    const closeButton = document.querySelector('[data-chatbot-close]');
    const form = document.querySelector('[data-chatbot-form]');
    const input = document.querySelector('[data-chatbot-input]');
    const messages = document.querySelector('[data-chatbot-messages]');
    const faqContainer = document.querySelector('[data-chatbot-faqs]');
    const ticketToggle = document.querySelector('[data-chatbot-ticket-toggle]');
    const ticketBox = document.querySelector('[data-chatbot-ticket]');
    const ticketForm = document.querySelector('[data-chatbot-ticket-form]');

    if (!launcher || !panel || !form || !input || !messages) return;

    function openChat() {
        panel.classList.add('is-open');
        input.focus();
    }

    function closeChat() {
        panel.classList.remove('is-open');
    }

    function appendMessage(text, role) {
        const message = document.createElement('div');
        message.className = `chat-message ${role}`;
        message.textContent = text;
        messages.appendChild(message);
        messages.scrollTop = messages.scrollHeight;
        return message;
    }

    function appendTyping() {
        const wrapper = document.createElement('div');
        wrapper.className = 'chat-message bot typing';
        wrapper.innerHTML = '<span></span><span></span><span></span>';
        messages.appendChild(wrapper);
        messages.scrollTop = messages.scrollHeight;
        return wrapper;
    }

    function renderFaqs(suggestions) {
        if (!faqContainer || !Array.isArray(suggestions)) return;
        faqContainer.innerHTML = '';
        suggestions.slice(0, 5).forEach((suggestion) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'chatbot-faq';
            button.textContent = suggestion;
            button.addEventListener('click', () => askQuestion(suggestion));
            faqContainer.appendChild(button);
        });
    }

    async function askQuestion(question) {
        const text = question.trim();
        if (!text) return;

        appendMessage(text, 'user');
        input.value = '';
        const typing = appendTyping();

        try {
            const response = await fetch('/api/support/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await response.json();
            typing.remove();
            appendMessage(data.answer || 'I could not find an answer right now.', 'bot');
            renderFaqs(data.suggestions);
        } catch (error) {
            typing.remove();
            appendMessage('Support is temporarily unavailable. Please try again in a moment.', 'bot');
        }
    }

    launcher.addEventListener('click', openChat);
    closeButton?.addEventListener('click', closeChat);
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        askQuestion(input.value);
    });

    ticketToggle?.addEventListener('click', () => {
        ticketBox?.classList.toggle('is-open');
    });

    ticketForm?.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(ticketForm);
        const message = formData.get('message');
        const email = formData.get('email');
        const subject = formData.get('subject');

        try {
            const response = await fetch('/api/support/ticket', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, email, subject })
            });
            const data = await response.json();
            appendMessage(data.message || data.error, response.ok ? 'bot' : 'bot');
            if (response.ok) {
                ticketForm.reset();
                ticketBox?.classList.remove('is-open');
            }
        } catch (error) {
            appendMessage('Ticket creation failed. Please try again.', 'bot');
        }
    });

    document.querySelectorAll('[data-chatbot-faqs] .chatbot-faq').forEach((button) => {
        button.addEventListener('click', () => askQuestion(button.textContent || ''));
    });

    document.querySelectorAll('.support-suggestion').forEach((button) => {
        button.addEventListener('click', () => {
            openChat();
            askQuestion(button.dataset.question || button.textContent);
        });
    });
})();
