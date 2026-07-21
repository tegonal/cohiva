(function () {
    let dirty = false;

    document.addEventListener("change", () => { dirty = true; });
    document.addEventListener("submit", () => { dirty = false; });

    window.addEventListener("beforeunload", (e) => {
        if (dirty) {
            e.preventDefault();
        }
    });
})();