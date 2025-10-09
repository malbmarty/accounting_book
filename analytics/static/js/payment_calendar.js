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