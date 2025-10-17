document.getElementById('paymentCalendarForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const form = e.target;
    const params = new URLSearchParams({
        start_date: form.start_date.value,
        end_date: form.end_date.value,
        project: form.project.value,
        period_type: form.period_type.value
    });
    window.location.href = `/analytics/payment-calendar/?${params.toString()}`;
});

document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.dropdown').forEach(function (dropdown) {
    const toggle = dropdown.querySelector('.dropdown-toggle');
    const menu = dropdown.querySelector('.dropdown-menu');
    const hidden = dropdown.querySelector('input[type="hidden"]');

    toggle.addEventListener('click', function () {
      menu.classList.toggle('open');
    });

    menu.addEventListener('click', function (e) {
      const item = e.target.closest('.dropdown-item');
      if (!item) return;
      const value = item.dataset.value;
      const label = item.textContent.trim();

      hidden.value = value;
      toggle.textContent = label;
      menu.classList.remove('open');
    });

    document.addEventListener('click', function (e) {
      if (!dropdown.contains(e.target)) {
        menu.classList.remove('open');
      }
    });
  });
});