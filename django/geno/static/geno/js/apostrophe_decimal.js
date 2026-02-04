document.addEventListener("DOMContentLoaded", function () {
    // Track recent pointer interactions so we can distinguish keyboard focus
    // (Tab) from mouse/pointer focus (click). This helps us open the editor
    // automatically on keyboard focus but avoid double-opening when the user
    // actually clicked with the pointer.
    if (!window.__apostropheLastPointerTime) {
        window.__apostropheLastPointerTime = 0;
        document.addEventListener('pointerdown', function () { window.__apostropheLastPointerTime = Date.now(); }, true);
    }

    // Helper: format number with apostrophe thousands and dot decimal (2 digits)
    function formatWithApostrophe(value, decimals) {
        if (value === null || value === undefined || value === "") return "";
        var n = Number(value);
        if (isNaN(n)) return value;
        decimals = (typeof decimals === 'number' && decimals >= 0) ? decimals : 2;
        var parts = n.toFixed(decimals).split('.');
        var intPart = parts[0];
        var decPart = parts[1] || '';
        // add apostrophe as thousand separator
        intPart = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, "'");
        return decPart ? (intPart + '.' + decPart) : intPart;
    }

    // Helper: compute decimal places from input's attributes (step, data-decimals)
    function computeDecimalsFromInput(inp) {
        // priority: data-decimals attribute, then step attribute, else default 2
        try {
            var dd = inp.getAttribute('data-decimals');
            if (dd !== null && dd !== undefined && dd !== '') {
                var ddi = parseInt(dd, 10);
                if (!isNaN(ddi) && ddi >= 0) return ddi;
            }
            var step = inp.getAttribute('step');
            if (step === null || step === undefined || step === '' || step.toLowerCase() === 'any') {
                // if no step attr, try to infer from existing value
                var existing = inp.value;
                if (existing && String(existing).indexOf('.') >= 0) {
                    return String(existing).split('.')[1].length;
                }
                return 2;
            }
            // handle exponential format like 1e-2
            var m = String(step).match(/e-(\d+)/i);
            if (m) return parseInt(m[1], 10);
            if (String(step).indexOf('.') >= 0) {
                return String(step).split('.')[1].length;
            }
            // fallback: try numeric conversion
            var num = Number(step);
            if (!isNaN(num) && isFinite(num)) {
                var s = num.toString();
                if (s.indexOf('.') >= 0) return s.split('.')[1].length;
            }
        } catch (e) {}
        return 2;
    }

    // Helper: parse user input (accept apostrophes, spaces, commas, dot)
    function parseUserNumber(str) {
        if (str === null || str === undefined) return null;
        str = String(str).trim();
        if (str === "") return null;
        // remove apostrophes and spaces
        str = str.replace(/'/g, '').replace(/\s/g, '');
        // replace comma with dot
        str = str.replace(/,/g, '.');
        // if multiple dots, keep last as decimal separator
        var dotCount = (str.match(/\./g) || []).length;
        if (dotCount > 1) {
            var lastDot = str.lastIndexOf('.');
            var integer = str.slice(0, lastDot).replace(/\./g, '');
            var decimal = str.slice(lastDot + 1);
            str = integer + '.' + decimal;
        }
        var n = Number(str);
        if (isNaN(n)) return null;
        return n;
    }

    // Helper: clean input string preserving user's typed fractional digits
    function cleanInputString(str) {
        if (str === null || str === undefined) return '';
        var s = String(str).trim();
        if (s === '') return '';
        s = s.replace(/'/g, '').replace(/\s/g, '');
        s = s.replace(/,/g, '.');
        var dotCount = (s.match(/\./g) || []).length;
        if (dotCount > 1) {
            var lastDot = s.lastIndexOf('.');
            var integer = s.slice(0, lastDot).replace(/\./g, '');
            var decimal = s.slice(lastDot + 1);
            s = integer + '.' + decimal;
        }
        // normalize leading/trailing dots
        if (s === '.') return '';
        if (s[0] === '.') s = '0' + s;
        if (s[s.length - 1] === '.') s = s.slice(0, -1);
        return s;
    }

    // Helper: validate an edit string against the original input's constraint attributes
    function validateAgainstOriginal(editStr, origInput) {
        // returns { valid: boolean, message: string }
        var parsed = parseUserNumber(editStr);
        // required
        if (origInput.hasAttribute('required')) {
            if (parsed === null) return { valid: false, message: 'Value is required' };
        }
        if (parsed === null) return { valid: true, message: '' }; // empty and not required

        // numeric checks
        var minAttr = origInput.getAttribute('min');
        if (minAttr !== null && minAttr !== undefined && minAttr !== '') {
            var minVal = Number(minAttr);
            if (!isNaN(minVal) && parsed < minVal) return { valid: false, message: 'Value is lower than minimum' };
        }
        var maxAttr = origInput.getAttribute('max');
        if (maxAttr !== null && maxAttr !== undefined && maxAttr !== '') {
            var maxVal = Number(maxAttr);
            if (!isNaN(maxVal) && parsed > maxVal) return { valid: false, message: 'Value is greater than maximum' };
        }
        // step check (if present)
        var stepAttr = origInput.getAttribute('step');
        if (stepAttr !== null && stepAttr !== undefined && stepAttr !== '') {
            var stepVal = Number(stepAttr);
            if (!isNaN(stepVal) && stepVal > 0) {
                // compute remainder relative to min or 0
                var base = 0;
                var minBase = origInput.getAttribute('min');
                if (minBase !== null && minBase !== undefined && minBase !== '') {
                    var mb = Number(minBase);
                    if (!isNaN(mb)) base = mb;
                }
                // allow small float errors
                var remainder = Math.abs((parsed - base) / stepVal - Math.round((parsed - base) / stepVal));
                if (remainder > 1e-8) return { valid: false, message: 'Value does not match step increments' };
            }
        }

        // pattern check (use the raw edit string, not parsed)
        var pattern = origInput.getAttribute('pattern');
        if (pattern) {
            try {
                var re = new RegExp('^(?:' + pattern + ')$');
                if (!re.test(editStr)) return { valid: false, message: 'Value does not match required pattern' };
            } catch (e) {
                // invalid pattern attribute, ignore
            }
        }

        // maxlength/minlength
        var maxlength = origInput.getAttribute('maxlength');
        if (maxlength) {
            var ml = parseInt(maxlength, 10);
            if (!isNaN(ml) && String(editStr).length > ml) return { valid: false, message: 'Value exceeds maximum length' };
        }
        var minlength = origInput.getAttribute('minlength');
        if (minlength) {
            var mnl = parseInt(minlength, 10);
            if (!isNaN(mnl) && String(editStr).length < mnl) return { valid: false, message: 'Value is shorter than minimum length' };
        }

        return { valid: true, message: '' };
    }

    // Apply to all inputs that opt-in via data-apostrophe="1"
    var inputs = document.querySelectorAll('input[data-apostrophe="1"]');
    // keep track of forms we've attached a submit handler to to avoid duplicates
    if (!window.__apostropheDecimalForms) window.__apostropheDecimalForms = new WeakSet();
    inputs.forEach(function (origInput) {
        // determine decimals for this input from its attributes
        var decimals = computeDecimalsFromInput(origInput);
         // ensure we have a form
         var form = origInput.form;
        // create a display span to show formatted value
        var display = document.createElement('span');
        display.className = 'apostrophe-display';
        display.style.cursor = 'text';
        display.style.display = 'inline-block';
        // make interactions reliable
        display.setAttribute('role', 'textbox');
        display.setAttribute('aria-readonly', 'false');
        display.title = origInput.getAttribute('placeholder') || 'Click to edit';
        display.style.pointerEvents = 'auto';
        // copy computed width from input to keep layout stable
        display.style.minWidth = (origInput.offsetWidth ? origInput.offsetWidth + 'px' : '6em');

        // copy some visual cues from the original input so the span looks like an editable field
        try {
            var cs = window.getComputedStyle(origInput);

            // helper: find effective (non-transparent) background color by walking up ancestors
            function findEffectiveBackgroundColor(el) {
                var node = el;
                while (node && node !== document.documentElement) {
                    try {
                        var c = window.getComputedStyle(node).backgroundColor;
                        if (c && c !== 'transparent' && c !== 'rgba(0, 0, 0, 0)') return c;
                    } catch (e) {
                        // ignore
                    }
                    node = node.parentElement;
                }
                // fallback to body or white
                var bodyBg = window.getComputedStyle(document.body).backgroundColor || 'rgb(255,255,255)';
                return bodyBg;
            }

            function parseRGB(colorStr) {
                // supports rgb(), rgba(), hex (#rrggbb) rarely returned by computedStyle but handle rgb
                var m = colorStr.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/i);
                if (m) return [parseInt(m[1], 10), parseInt(m[2], 10), parseInt(m[3], 10)];
                // hex
                m = colorStr.match(/#([0-9a-f]{6})/i);
                if (m) {
                    var hex = m[1];
                    return [parseInt(hex.slice(0,2),16), parseInt(hex.slice(2,4),16), parseInt(hex.slice(4,6),16)];
                }
                return null;
            }

            function luminance(rgb) {
                // rgb array [r,g,b]
                var s = rgb.map(function (v) {
                    var c = v / 255;
                    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
                });
                return 0.2126 * s[0] + 0.7152 * s[1] + 0.0722 * s[2];
            }

            var effectiveBg = findEffectiveBackgroundColor(origInput) || cs.backgroundColor || 'rgb(255,255,255)';
            var rgb = parseRGB(effectiveBg) || [255,255,255];
            var lum = luminance(rgb);
            var isDark = lum < 0.5;

            display.style.padding = cs.padding || '0.5rem 0.75rem';
            display.style.borderRadius = cs.borderRadius || '0.375rem';
            if (isDark) {
                // stronger, high-contrast defaults for dark theme
                try { display.style.setProperty('background-color', '#0f1724', 'important'); } catch (e) { display.style.backgroundColor = '#0f1724'; }
                try { display.style.setProperty('border', '1px solid #374151', 'important'); } catch (e) { display.style.border = '1px solid #374151'; }
                // force contrasting text color
                display._contrastingColor = '#e6eef8';
            } else {
                // stronger, high-contrast defaults for light theme
                try { display.style.setProperty('background-color', '#ffffff', 'important'); } catch (e) { display.style.backgroundColor = '#ffffff'; }
                try { display.style.setProperty('border', '1px solid #e2e8f0', 'important'); } catch (e) { display.style.border = '1px solid #e2e8f0'; }
                display._contrastingColor = '#0f172a';
            }
            // set base text color and ensure visibility
            try { display.style.setProperty('color', display._contrastingColor, 'important'); } catch (e) { display.style.color = display._contrastingColor; }
            try { display.style.setProperty('visibility', 'visible', 'important'); } catch (e) { display.style.visibility = 'visible'; }
            try { display.style.setProperty('opacity', '1', 'important'); } catch (e) { display.style.opacity = '1'; }
            try { display.style.setProperty('z-index', '999', 'important'); } catch (e) { display.style.zIndex = '999'; }
        } catch (e) {
            // ignore; fall back to sensible defaults
            display.style.padding = '0.5rem 0.75rem';
            display.style.border = '1px solid rgba(0,0,0,0.08)';
            display.style.borderRadius = '0.375rem';
            display.style.backgroundColor = 'rgba(0,0,0,0.02)';
            display.style.color = '#111';
        }
        // keep text on one line and ellipsize if too long
        display.style.whiteSpace = 'nowrap';
        display.style.overflow = 'hidden';
        display.style.textOverflow = 'ellipsis';

        // hide original input visually but keep it in DOM for submission
        // using display:none can sometimes collapse layout or interact poorly with CSS; instead
        // position the input off-screen so it remains in the DOM and available for form submit
        origInput.style.position = 'absolute';
        origInput.style.left = '-9999px';
        origInput.style.width = '1px';
        origInput.style.height = '1px';
        origInput.style.overflow = 'hidden';
        origInput.style.clip = 'rect(0 0 0 0)';
        origInput.style.border = '0';
        origInput.style.padding = '0';
        origInput.style.margin = '0';
        // remove the original input from the Tab order so keyboard Tab focuses the visible span
        try { origInput.tabIndex = -1; } catch (e) {}

        // insert display before the original input
        origInput.parentNode.insertBefore(display, origInput);

        // If the original input receives focus (for example via its label), open the editor.
        // This preserves label 'for' behavior while keeping the original input off-screen.
        origInput.addEventListener('focus', function () {
            // forward focus to the visible display so Tab lands there. Do not open the
            // editor immediately (click), let keyboard users press Enter/Space to edit.
            try {
                display.focus();
            } catch (e) {}
        });

        // make display keyboard-accessible so empty fields can be focused/activated
        display.tabIndex = 0;

        // debugging aid: confirm initialization in browser console
        try { console.log('apostrophe_decimal: initialized for', origInput.id || origInput.name); } catch (e) {}

        function refreshDisplay() {
            var v = origInput.value;
            if (v === null || v === undefined || v === '') {
                // show placeholder or a short dash so the span is visible and users know they can edit
                var placeholder = origInput.getAttribute('placeholder') || '-';
                display.textContent = placeholder;
                // use a dimmed text color for placeholder but keep border visible
                try {
                    if (display._contrastingColor) {
                        if (display._contrastingColor === '#ffffff') {
                            display.style.setProperty('color', 'rgba(255,255,255,0.85)', 'important');
                        } else {
                            display.style.setProperty('color', 'rgba(0,0,0,0.65)', 'important');
                        }
                    } else {
                        display.style.opacity = '0.85';
                    }
                } catch (e) {
                    display.style.opacity = '0.85';
                }
                try { display.style.setProperty('visibility', 'visible', 'important'); } catch (e) { display.style.visibility = 'visible'; }
                try { display.style.setProperty('opacity', display.style.opacity || '0.85', 'important'); } catch (e) {}
            } else {
                // Determine decimals: only pad to a fixed precision when data-decimals
                // is explicitly provided by the server. Otherwise preserve the user's
                // entered precision by deriving the decimal length from the value string.
                var d;
                if (origInput.hasAttribute('data-decimals')) {
                    d = computeDecimalsFromInput(origInput);
                } else {
                    var sval = String(v);
                    if (sval.indexOf('.') >= 0) {
                        d = sval.split('.')[1].length;
                    } else {
                        d = 0;
                    }
                }
                // Try to parse the value into a number first so formatting is reliable
                var parsedVal = parseUserNumber(v);
                if (parsedVal !== null) {
                    display.textContent = formatWithApostrophe(parsedVal, d);
                } else {
                    // fallback: let formatWithApostrophe try (it will return the original string if it cannot parse)
                    display.textContent = formatWithApostrophe(v, d);
                }
                 // restore strong text color when value is present
                 if (display._contrastingColor) display.style.color = display._contrastingColor;
                 display.style.opacity = '1';
                 try { display.style.setProperty('visibility', 'visible', 'important'); } catch (e) { display.style.visibility = 'visible'; }
             }
         }

        refreshDisplay();

        // When clicking the display, switch to an editable text input
        display.addEventListener('click', function () {
            // create edit input as a number field so users get numeric keyboard/controls
            var edit = document.createElement('input');
            edit.type = 'number';
            edit.className = origInput.className || '';
            // Important: do NOT copy submission/validation attributes from the original input.
            // The original input (the one generated by Django/models.py) contains all
            // server-side and client-side validation attributes (name, id, required,
            // min, max, step, pattern, maxlength, etc.). We must not overwrite those
            // requirements. Keep the edit input purely presentational.
            // Ensure edit input has no name/id and no validation attributes.
            try {
                edit.removeAttribute('name');
                edit.removeAttribute('id');
                edit.removeAttribute('required');
                edit.removeAttribute('min');
                edit.removeAttribute('max');
                edit.removeAttribute('pattern');
                edit.removeAttribute('maxlength');
                edit.removeAttribute('minlength');
                edit.removeAttribute('step');
                edit.removeAttribute('aria-required');
                edit.removeAttribute('disabled');
            } catch (e) {}
            // mark for debugging so we can find this element in DOM if needed
            edit.dataset.apostropheEdit = '1';
            // copy some attributes for accessibility
            edit.setAttribute('aria-label', origInput.getAttribute('aria-label') || '');
            // prefer decimal keyboard on mobile and allow 2 decimal steps
            edit.setAttribute('inputmode', 'decimal');
            // set step according to computed decimals (so we don't force 2 decimals)
            try {
                var editDecimals = computeDecimalsFromInput(origInput);
                var stepStr = (editDecimals === 0) ? '1' : ('0.' + new Array(editDecimals).join('0') + '1');
                edit.setAttribute('step', stepStr);
            } catch (e) {
                edit.setAttribute('step', '0.01');
            }
            // set style to keep layout stable
            edit.style.minWidth = display.style.minWidth;

            // set value to the raw numeric value (no thousands separator) so user edits XXXX.XX
            // If the user started typing while the display had focus we stored the
            // initial key on display._initialKey above; consume that so typing
            // immediately produces characters in the editor.
            var currentVal = origInput.value;
            if (display._initialKey !== undefined) {
                var ik = display._initialKey;
                try { delete display._initialKey; } catch (e) { display._initialKey = undefined; }
                if (ik === 'Backspace' || ik === 'Delete') {
                    edit.value = '';
                } else {
                    var ch = (ik === ',') ? '.' : ik;
                    // start a fresh value when typing after focusing
                    edit.value = String(ch);
                }
            } else {
                edit.value = (currentVal === null || currentVal === undefined) ? '' : currentVal;
            }

            // Compute focusable elements now (while display is still in the DOM), so we
            // can determine the correct next/previous target when the user presses Tab
            // while editing. We build a robust list using the element.tabIndex property
            // and visibility checks so that both attribute and property-based tabindexes
            // are respected.
            var rootForFocus = form || document;
            function isVisible(el) {
                try {
                    if (el.offsetWidth > 0 || el.offsetHeight > 0) return true;
                    if (el.getClientRects && el.getClientRects().length) return true;
                } catch (e) {}
                return false;
            }
            function isElementFocusable(el) {
                if (!el) return false;
                if (el.disabled) return false;
                var tn = el.tagName && el.tagName.toLowerCase();
                // naturally focusable elements
                var naturally = ['a','input','select','textarea','button','iframe'];
                if (tn === 'a' && el.hasAttribute('href')) {
                    // anchor with href
                } else if (naturally.indexOf(tn) === -1) {
                    // not a natural element, allow if tabindex >= 0 or contentEditable
                    if (typeof el.tabIndex === 'number' && el.tabIndex >= 0) return isVisible(el);
                    if (el.isContentEditable) return isVisible(el);
                    return false;
                }
                // natural controls: ensure not disabled and visible
                // treat elements with explicit tabindex="-1" as not focusable
                return isVisible(el) && (el.tabIndex === undefined || el.tabIndex >= 0);
            }
            // gather in-document order and include the visible display at its real
            // document position so stepping from it yields the correct neighbors.
            var all = Array.prototype.slice.call(rootForFocus.querySelectorAll('*'));
            var storedFocusables = [];
            var displayIndexInList = -1;
            for (var ii = 0; ii < all.length; ii++) {
                var el = all[ii];
                if (el === display) {
                    displayIndexInList = storedFocusables.length;
                    storedFocusables.push(display);
                    continue;
                }
                if (isElementFocusable(el)) {
                    storedFocusables.push(el);
                }
            }
            // If display wasn't seen (edge cases), append it
            if (displayIndexInList === -1) {
                displayIndexInList = storedFocusables.length;
                storedFocusables.push(display);
            }

            // guard to prevent double finish calls from blur + Tab interactions
            var finishing = false;

            // replace display with edit
            display.parentNode.replaceChild(edit, display);
            edit.focus();
            // ensure the edit field inherits proper size and visibility
            try { edit.style.setProperty('color', window.getComputedStyle(display).color, 'important'); } catch (e) {}

            // while editing, keep the hidden original input synchronized so a form submit while
            // the visible editor is still focused will submit a sane value.
            function syncToOriginal() {
                // While editing we will keep the original input's value in a cleaned form
                // preserving the user's entered precision rather than forcing padding.
                var cleaned = cleanInputString(edit.value);
                origInput.value = cleaned;
             }

            // on blur or Tab, parse and write back to original input and restore display
            // Define finish here so it closes over edit, origInput, display and can accept
            // an optional nextFocus element (used by Tab navigation).
            function finish(nextFocus, forceMove) {
                if (finishing) return; // already running
                finishing = true;
                // validate against original input constraints before committing
                var validation = validateAgainstOriginal(edit.value, origInput);
                if (!validation.valid) {
                    if (!forceMove) {
                        // show invalid state on edit and keep it open for correction
                        try {
                            edit.setAttribute('aria-invalid', 'true');
                            edit.title = validation.message;
                            edit.style.border = '1px solid #dc2626'; // red
                            edit.focus();
                        } catch (e) {}
                        finishing = false;
                        return;
                    } else {
                        // mark as invalid but proceed with commit and move focus
                        try {
                            edit.setAttribute('aria-invalid', 'true');
                            edit.title = validation.message;
                            edit.style.border = '1px solid #dc2626';
                        } catch (e) {}
                    }
                }

                 // commit sanitized value to the hidden original input and restore display
                 edit.removeAttribute('aria-invalid');
                 edit.title = '';
                // If the original input explicitly defines decimals via data-decimals,
                // pad to that precision. Otherwise preserve the user's typed precision.
                var cleaned = cleanInputString(edit.value);
                var shouldPad = origInput.hasAttribute('data-decimals');
                if (shouldPad) {
                    var parsed = parseUserNumber(edit.value);
                    if (parsed === null) {
                        origInput.value = '';
                    } else {
                        var dcommit = computeDecimalsFromInput(origInput);
                        origInput.value = parsed.toFixed(dcommit);
                    }
                } else {
                    origInput.value = cleaned;
                }
                // restore display
                // compute formatted text to ensure the display always shows the apostrophe format
                var formattedText = '';
                try {
                    var vForFormat = origInput.value;
                    var parsedForFormat = parseUserNumber(vForFormat);
                    var decimalsForFormat = 0;
                    if (origInput.hasAttribute('data-decimals')) {
                        decimalsForFormat = computeDecimalsFromInput(origInput);
                    } else {
                        if (String(vForFormat).indexOf('.') >= 0) decimalsForFormat = String(vForFormat).split('.')[1].length;
                        else decimalsForFormat = 0;
                    }
                    if (parsedForFormat !== null) {
                        formattedText = formatWithApostrophe(parsedForFormat, decimalsForFormat);
                    } else {
                        formattedText = vForFormat;
                    }
                } catch (e) {
                    formattedText = origInput.value;
                }
                edit.parentNode.replaceChild(display, edit);
                // apply the computed formatted text immediately to avoid a transient unformatted state
                try { display.textContent = formattedText; } catch (e) {}
                // then run the normal refresh to restore colors/visibility etc.
                refreshDisplay();
                // If a next focus target was provided (e.g., via Tab), focus it after DOM update.
                setTimeout(function () {
                    try {
                        if (nextFocus) {
                            try { nextFocus.focus(); } catch (e) {}
                            // If focus succeeded, we're done
                            if (document.activeElement === nextFocus) return;
                        }
                        // Otherwise recompute tabbable elements now that the DOM has been updated
                        var selectorNow = 'a[href], area[href], input:not([tabindex="-1"]):not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), iframe, [tabindex]:not([tabindex="-1"]), [contentEditable=true]';
                        var rootNow = form || document;
                        var nodesNow = Array.prototype.slice.call(rootNow.querySelectorAll('*'));
                        var focusablesNow = [];
                        var displayIdxNow = -1;
                        for (var zi = 0; zi < nodesNow.length; zi++) {
                            var zel = nodesNow[zi];
                            if (zel === display) {
                                displayIdxNow = focusablesNow.length;
                                focusablesNow.push(display);
                                continue;
                            }
                            try {
                                if (isElementFocusable(zel)) focusablesNow.push(zel);
                            } catch (e) {}
                        }
                        if (displayIdxNow === -1) {
                            displayIdxNow = focusablesNow.indexOf(display);
                        }
                        var nextCandidate = null;
                        if (displayIdxNow >= 0) {
                            for (var yi = displayIdxNow + 1; yi < focusablesNow.length; yi++) {
                                var candNow = focusablesNow[yi];
                                if (!candNow) continue;
                                if (candNow === origInput) continue;
                                if (candNow === display) continue;
                                try { if (candNow.offsetWidth === 0 && candNow.offsetHeight === 0) continue; } catch (e) {}
                                nextCandidate = candNow; break;
                            }
                        }
                        if (nextCandidate) {
                            try { nextCandidate.focus(); } catch (e) {}
                        }
                    } catch (e) {}
                }, 0);
                finishing = false;
            }

            // handle input events to update display immediately with raw value (no formatting)
            // and synchronize the hidden original input for form submission.
            // We do NOT use the 'change' event here because that would introduce a delay
            // and require an extra user action (blur) to commit the value.
            // Note: input events fire in the order: keydown -> input -> (optional) change -> blur
            // We need to be careful about focus management and not interfere with user typing.
            edit.addEventListener('keydown', function (e) {
                // Ignore keydown here, we only need input event for updates
            });
            edit.addEventListener('input', function (e) {
                // immediate refresh display with raw value (no formatting)
                var v = edit.value;
                if (v === null || v === undefined || v === '') {
                    // show placeholder or a short dash so the span is visible and users know they can edit
                    var placeholder = origInput.getAttribute('placeholder') || '-';
                    display.textContent = placeholder;
                    // use a dimmed text color for placeholder but keep border visible
                    try {
                        if (display._contrastingColor) {
                            if (display._contrastingColor === '#ffffff') {
                                display.style.setProperty('color', 'rgba(255,255,255,0.85)', 'important');
                            } else {
                                display.style.setProperty('color', 'rgba(0,0,0,0.65)', 'important');
                            }
                        } else {
                            display.style.opacity = '0.85';
                        }
                    } catch (e) {
                        display.style.opacity = '0.85';
                    }
                } else {
                    // show the raw typed value in the display while editing so users see
                    // exactly what they typed (no apostrophe thousand separators)
                    try {
                        display.style.setProperty('color', window.getComputedStyle(edit).color, 'important');
                    } catch (e) {}
                    display.textContent = v;
                    display.style.opacity = '1';
                }
                // keep original input synchronized for form submit
                try { syncToOriginal(); } catch (e) {}
            });

            // ----- START: new handlers to finish editing on blur / Tab / Enter / Escape -----
            // When the edit loses focus (e.g. the user clicked another control), commit and
            // move focus to whatever element received focus. Use setTimeout(0) so the
            // browser has a chance to update document.activeElement first.
            edit.addEventListener('blur', function () {
                setTimeout(function () {
                    try { finish(document.activeElement, true); } catch (e) {}
                }, 0);
            });

            // Handle keyboard navigation while editing. We need to intercept Tab so the
            // browser doesn't move focus before we commit and compute the proper next target.
            edit.addEventListener('keydown', function (e) {
                // Tab: commit and move to next/previous focusable
                if (e.key === 'Tab') {
                    e.preventDefault();
                    var dir = e.shiftKey ? -1 : 1;
                    var next = null;
                    if (typeof displayIndexInList === 'number' && storedFocusables && storedFocusables.length) {
                        var start = displayIndexInList;
                        var idx = start;
                        for (var t = start + dir; (dir > 0) ? (t < storedFocusables.length) : (t >= 0); t += dir) {
                            var cand = storedFocusables[t];
                            if (!cand) continue;
                            if (cand === origInput) continue;
                            if (cand === display) continue;
                            try { if (cand.offsetWidth === 0 && cand.offsetHeight === 0) continue; } catch (err) {}
                            next = cand; break;
                        }
                    }
                    finish(next, true);
                    return;
                }
                // Enter: commit and keep focus where appropriate
                if (e.key === 'Enter') {
                    e.preventDefault();
                    finish(null, false);
                    return;
                }
                // Escape: cancel editing and restore display without committing
                if (e.key === 'Escape') {
                    try {
                        // replace editor with display and restore previous visual
                        edit.parentNode.replaceChild(display, edit);
                        refreshDisplay();
                        try { display.focus(); } catch (e) {}
                    } catch (err) {}
                    return;
                }
            });
            // ----- END: new handlers -----

            // end of click handler: we already attached key/blur/input listeners, so close it
        });

        // allow keyboard activation to open the editor as well. In addition to
        // Enter/Space, open the editor when the user types a numeric character
        // (0-9), decimal separator (dot/comma), negative sign or Backspace/Delete.
        // We capture the initial key on the display and then consume it when the
        // editor is created so typing immediately starts editing without a mouse.
        display.addEventListener('keydown', function (ev) {
            var k = ev.key;
            if (k === 'Enter' || k === ' ') {
                ev.preventDefault();
                display.click();
                return;
            }
            // allow digits, decimal point/comma, minus sign, Backspace/Delete
            var isDigit = /^[0-9]$/.test(k);
            var isDecimal = (k === '.' || k === ',');
            var isMinus = (k === '-' || k === '−');
            var isErase = (k === 'Backspace' || k === 'Delete');
            if (isDigit || isDecimal || isMinus || isErase) {
                // prevent the key from doing anything on the span and open editor
                ev.preventDefault();
                // store initial key for the click handler to consume
                try { display._initialKey = k; } catch (e) {}
                display.click();
            }
        });

        // add visible focus styling so keyboard users can see the span is active
        display.addEventListener('focus', function () {
            // use a subtle boxShadow to indicate focus (similar to focus ring)
            display.style.boxShadow = '0 0 0 3px rgba(59,130,246,0.15)';
            display.style.borderRadius = '4px';
            // Open the editor on focus so keyboard users (Tab) can start typing
            // immediately; schedule it to the next tick so focus/key ordering
            // has a chance to settle.
            try {
                setTimeout(function () {
                    try { if (display.parentNode) display.click(); } catch (e) {}
                }, 0);
            } catch (e) {}
        });
         display.addEventListener('blur', function () {
             display.style.boxShadow = '';
         });

        // Ensure on form submit the original inputs contain sanitized numeric values.
        // Attach a single submit handler per form (use a WeakSet on window to remember)
        if (form && !window.__apostropheDecimalForms.has(form)) {
            window.__apostropheDecimalForms.add(form);
            form.addEventListener('submit', function () {
                var toSanitize = form.querySelectorAll('input[data-apostrophe="1"]');
                toSanitize.forEach(function (i) {
                     var parsed = parseUserNumber(i.value);
                     if (parsed === null) {
                         i.value = '';
                     } else {
                        // If the input explicitly declares decimals, format to that precision.
                        // Otherwise preserve the user's precision (clean string).
                        var shouldPadI = i.hasAttribute('data-decimals');
                        if (shouldPadI) {
                            var dec = computeDecimalsFromInput(i);
                            i.value = parsed.toFixed(dec);
                        } else {
                            i.value = cleanInputString(i.value);
                        }
                     }
                 });
             });
         }
     });
 });
