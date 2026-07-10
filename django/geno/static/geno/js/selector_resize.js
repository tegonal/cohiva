/*
 * IIFE to automatically adjust the initial height of .selector elements, and
 * add CSS-native resize handles to the container.
 */
(function () {
    // Ensure all .selector elements have a height set at initialisation time
    function initSelectors() {
        document.querySelectorAll('.selector').forEach(function (el) {
            var h = el.getBoundingClientRect().height;
            if (h > 0 && !el.style.height) el.style.height = h * 1.2 + 'px';
        });
    }

    // Only execute after the DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSelectors);
    } else {
        initSelectors();
    }

    // Handle dynamically added .selector elements (e.g. inline formsets)
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
