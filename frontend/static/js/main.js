document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('input[type="password"]').forEach(input => {
    const toggle = input.closest('.password-control')?.querySelector('.password-toggle');
    if (!toggle) return;
    toggle.addEventListener('click', () => {
      const visible = input.type === 'password';
      input.type = visible ? 'text' : 'password';
      toggle.setAttribute('aria-label', visible ? 'Ẩn mật khẩu' : 'Hiện mật khẩu');
      toggle.setAttribute('aria-pressed', String(visible));
    });
  });
  document.querySelectorAll('[data-month-picker]').forEach(form => {
    const year = form.querySelector('[data-report-year]');
    form.querySelectorAll('[data-report-month]').forEach(button => {
      button.addEventListener('click', () => {
        form.querySelector('[name="month"]').value = `${year.value}-${button.dataset.reportMonth.padStart(2, '0')}`;
        form.requestSubmit();
      });
    });
  });
  const path = window.location.pathname;
  let best = null;
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.search) return;
    const target = new URL(link.href).pathname;
    if ((target === '/' ? path === '/' : path.startsWith(target)) && (!best || target.length > new URL(best.href).pathname.length)) best = link;
  });
  if (best) { best.classList.add('active'); best.setAttribute('aria-current', 'page'); }
  document.querySelectorAll('[data-ai-form]').forEach(form => form.addEventListener('submit', () => {
    form.querySelector('button[type="submit"]').disabled = true;
    const message = form.querySelector('.loading-message');
    if (message) message.hidden = false;
  }));
  document.querySelectorAll('[data-question]').forEach(button => button.addEventListener('click', () => {
    const input = document.getElementById('id_question');
    input.value = button.dataset.question; input.focus();
  }));
  document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
    const input = document.getElementById(button.dataset.copy);
    try { await navigator.clipboard.writeText(input.value); button.textContent = 'Đã sao chép'; }
    catch { input.focus(); input.select(); button.textContent = 'Nhấn Ctrl+C để sao chép'; }
  }));
});
