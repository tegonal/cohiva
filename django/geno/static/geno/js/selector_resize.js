(function () {
    function initSelectors() {
        document.querySelectorAll('.selector').forEach(function (el) {
            var h = el.getBoundingClientRect().height;
            if (h > 0 && !el.style.height) el.style.height = h + 'px';
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSelectors);
    } else {
        initSelectors();
    }

    // Pin height for selectors added later (inline formsets)
    var observer = new MutationObserver(function (mutations) {
        var needsInit = false;
        mutations.forEach(function (m) {
            m.addedNodes.forEach(function (node) {
                if (node.nodeType === 1 &&
                    (node.classList.contains('selector') || node.querySelector('.selector'))) {
                    needsInit = true;
                }
            });
        });
        if (needsInit) initSelectors();
    });

    document.addEventListener('DOMContentLoaded', function () {
        observer.observe(document.body, { childList: true, subtree: true });
    });
})();
