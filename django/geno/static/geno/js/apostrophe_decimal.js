document.addEventListener("DOMContentLoaded", function () {
    const field = document.querySelector('input[name="rent_netto"]');
    if (!field) return;

    // Allow typing apostrophe (browser blocks it for type=number)
    field.setAttribute("type", "text");

    // Restore number input before submit
    field.form.addEventListener("submit", function () {
        field.value = field.value.replace(/'/g, "");
        field.setAttribute("type", "number");
    });
});