
function show_hide_fields() {
    var type = django.jQuery('select#id_template_type').find(":selected").val()
    console.log(type);
    if (type.startsWith("Email")) {
        django.jQuery('div.field-text').show();
        django.jQuery('div.field-file').hide();
        django.jQuery('div.field-template_context').hide();
        django.jQuery('div.field-manual_creation_allowed').hide();
    } else {
        django.jQuery('div.field-text').hide();
        django.jQuery('div.field-file').show();
        django.jQuery('div.field-manual_creation_allowed').show();
        if (type == "OpenDocument") {
            django.jQuery('div.field-template_context').show();
        } else {
            django.jQuery('div.field-template_context').hide();
        }
    }
}

jQuery(document).ready(function() {
    django.jQuery('select#id_template_type').change(function(){
        show_hide_fields()
    });
    show_hide_fields();
});

