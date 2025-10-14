/* Configure datepicker */
$(function() {
    $( ".datepicker" ).datepicker({
      changeMonth: true,
      changeYear: true,
      yearRange: "2010:2030",
      defaultDate: 0,
      dateFormat: "dd.mm.yy",
    });
});
/* Set focus to name field */
$(document).ready(function() {
    window.onload = function() {
      $("#id_name").focus();
    };
});
