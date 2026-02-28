(function(){
  // Generic focus/open behavior for admin autocomplete-like fields.
  // When a form row containing an autocomplete/search widget is clicked or activated
  // via keyboard (Enter/Space), this will focus the inner search input or open
  // the widget (Select2) so the user's next keystroke goes into the search box.

  var detectionSelectors = [
    '.select2-selection',
    'input.select2-search__field',      // Select2 search input
  ];

  function hasAutocompleteWidget(row){
    for(var i=0;i<detectionSelectors.length;i++){
      if(row.querySelector(detectionSelectors[i])) return true;
    }
    return false;
  }

  function focusAutocompleteInRow(row){
    if(!row) return;

    // If Select2 is used, open it and focus the search field
    var select2 = row.querySelector('.select2-container, .select2-selection');
    if(select2){
      try{ select2.click(); }catch(e){}
      setTimeout(function(){
        var s = select2.querySelector('.select2-search__field');
        if(s) { s.focus(); } else {
          try {
            document.querySelector('[aria-controls="select2-'+select2.parentElement.querySelector("select").id+'-results"]').focus();
          } catch(e) {
            // fallback: don't focus anything if the search field isn't found, to avoid focusing the wrong element
          }
        }
      }, 50);
      return;
    }
  }

  function filterAutocompleteInRow(target) {
    let row = target.closest('[class*="field-"]');
    if (!row) {
      // Try the "group" class (for custom forms)
      row = target.closest('.group');
    }
    if(!row) return;
    if(!hasAutocompleteWidget(row)) return;
    return row;
  }

  document.addEventListener('click', function(e){
    focusAutocompleteInRow(filterAutocompleteInRow(e.target));
  }, true);

  // allow keyboard activation when focusing label or row (Enter / Space)
  document.addEventListener('keydown', function(e){
    if(e.key !== 'Enter' && e.key !== ' ') return;
    focusAutocompleteInRow(filterAutocompleteInRow(e.target));
  }, true);
})();
