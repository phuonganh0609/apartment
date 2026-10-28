document.addEventListener('DOMContentLoaded', () => {
  const launcher = document.querySelector('.chat-launcher');
  if (launcher) {
    let drag = null;
    let suppressClick = false;
    const place = (left, top) => {
      const maxLeft = Math.max(0, window.innerWidth - launcher.offsetWidth - 8);
      const maxTop = Math.max(0, window.innerHeight - launcher.offsetHeight - 8);
      launcher.style.left = `${Math.max(8, Math.min(left, maxLeft))}px`;
      launcher.style.top = `${Math.max(8, Math.min(top, maxTop))}px`;
      launcher.style.right = 'auto'; launcher.style.bottom = 'auto';
    };
    launcher.addEventListener('pointerdown', event => {
      if (!event.isPrimary || event.button !== 0) return;
      suppressClick = false;
      const rect = launcher.getBoundingClientRect();
      drag = { id: event.pointerId, x: event.clientX, y: event.clientY, left: rect.left, top: rect.top, moved: false };
      launcher.setPointerCapture(event.pointerId);
    });
    launcher.addEventListener('pointermove', event => {
      if (!drag || event.pointerId !== drag.id) return;
      const dx = event.clientX - drag.x, dy = event.clientY - drag.y;
      if (!drag.moved && Math.hypot(dx, dy) < 6) return;
      drag.moved = true;
      launcher.classList.add('is-dragging');
      place(drag.left + dx, drag.top + dy);
    });
    const finish = event => {
      if (!drag || event.pointerId !== drag.id) return;
      suppressClick = drag.moved;
      launcher.classList.remove('is-dragging');
      if (launcher.hasPointerCapture(event.pointerId)) launcher.releasePointerCapture(event.pointerId);
      drag = null;
    };
    launcher.addEventListener('pointerup', finish);
    launcher.addEventListener('pointercancel', finish);
    launcher.addEventListener('lostpointercapture', () => { drag = null; launcher.classList.remove('is-dragging'); });
    launcher.addEventListener('click', event => {
      if (suppressClick) {
        event.preventDefault(); event.stopImmediatePropagation(); suppressClick = false;
      }
    }, true);
    window.addEventListener('resize', () => {
      if (launcher.style.left) {
        const rect = launcher.getBoundingClientRect(); place(rect.left, rect.top);
      }
    });
  }

  document.querySelectorAll('[data-chat-url]').forEach(root => {
    const form = root.querySelector('[data-chat-form]');
    const input = form.elements.question;
    const messages = root.querySelector('.chat-messages');
    const scrollArea = root.querySelector('.chat-scroll-area') || messages;
    const status = root.querySelector('[data-chat-status]');
    const send = form.querySelector('[type="submit"]');
    const add = (text, kind) => {
      const item = document.createElement('div');
      item.className = `chat-message ${kind === 'user' ? 'chat-message-user' : 'chat-message-assistant'}`;
      const label = document.createElement('strong');
      label.className = 'chat-message-author';
      label.textContent = kind === 'user' ? 'Bạn' : 'Trợ lý AI';
      const content = document.createElement('div');
      content.className = 'small'; content.style.whiteSpace = 'pre-wrap';
      content.textContent = text;
      item.append(label, content); messages.append(item);
      scrollArea.scrollTop = scrollArea.scrollHeight;
      return item;
    };
    root.querySelectorAll('[data-chat-suggestion]').forEach(button => {
      button.addEventListener('click', () => { input.value = button.textContent; input.focus(); });
    });
    input.addEventListener('keydown', event => {
      if (event.key === 'Enter' && !event.shiftKey && !event.isComposing && event.keyCode !== 229) {
        event.preventDefault();
        if (!send.disabled && input.value.trim()) form.requestSubmit();
      }
    });
    form.addEventListener('submit', async event => {
      event.preventDefault();
      const question = input.value.trim();
      if (!question || send.disabled) return;
      add(question, 'user'); send.disabled = true;
      status.textContent = 'Đang tìm tài liệu và tạo câu trả lời…';
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 100000);
      try {
        const response = await fetch(root.dataset.chatUrl, {
          method: 'POST', body: new FormData(form), credentials: 'same-origin',
          headers: { Accept: 'application/json' }, signal: controller.signal,
        });
        const data = await response.json();
        if (!response.ok || data.error) throw new Error(data.error || 'Không thể xử lý câu hỏi. Vui lòng thử lại.');
        const bubble = add(data.answer, 'assistant');
        (data.sources || []).forEach(source => {
          const details = document.createElement('details');
          const summary = document.createElement('summary');
          summary.textContent = `Nguồn: ${source.title}`;
          const text = document.createElement('p');
          text.className = 'small mt-2 mb-0'; text.textContent = source.text;
          details.append(summary, text); bubble.append(details);
        });
        input.value = ''; status.textContent = '';
      } catch (error) {
        add(error.name === 'AbortError' ? 'Dịch vụ phản hồi quá lâu. Vui lòng thử lại.' : (error instanceof SyntaxError ? 'Phiên đăng nhập hoặc dịch vụ không khả dụng. Vui lòng tải lại trang.' : error.message), 'assistant');
        status.textContent = 'Bạn có thể gửi lại câu hỏi.';
      } finally { clearTimeout(timer); send.disabled = false; scrollArea.scrollTop = scrollArea.scrollHeight; }
    });
  });
});
