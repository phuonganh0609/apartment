document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname;
  let best = null;
  document.querySelectorAll('.nav-link').forEach(link => {
    const target = new URL(link.href).pathname;
    if ((target === '/' ? path === '/' : path.startsWith(target)) && (!best || target.length > new URL(best.href).pathname.length)) best = link;
  });
  if (best) { best.classList.add('active'); best.setAttribute('aria-current', 'page'); }
  const menu = document.querySelector('.menu-toggle');
  if (menu) menu.addEventListener('click', () => {
    const open = document.getElementById('sidebar').classList.toggle('open');
    menu.setAttribute('aria-expanded', String(open));
  });
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
