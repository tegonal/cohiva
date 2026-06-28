import json

import jsonc

## Filer widget
# from django.contrib.admin.widgets import ForeignKeyRawIdWidget
# from django.template.loader import render_to_string
# from django.urls import reverse
# from django.utils.http import urlencode
# from django.utils.safestring import mark_safe
# from django.contrib.admin.sites import site
from django import forms
from django.core.exceptions import ValidationError

# JSONField from django.db.models is not a form field; use forms.JSONField instead.
# (No model-level JSONField import needed here.)
# from filer.fields.file import AdminFileFormField, FilerFileField, AdminFileWidget
from filer.models.filemodels import File as FilerFile

# Add Unfold widgets for consistent admin styling and focus behavior
from unfold.widgets import (
    UnfoldAdminDateWidget,
    UnfoldAdminDecimalFieldWidget,
    UnfoldAdminSelect2Widget,
    UnfoldAdminSelectWidget,
    UnfoldAdminTextareaWidget,
    UnfoldAdminTextInputWidget,
    UnfoldBooleanSwitchWidget,
)

import report.nk.cost_config
from geno.models import Building

from .models import ReportInputField, ReportItem

# class FilerFileWidget(AdminFileWidget):
#
#    def render(self, name, value, attrs=None, renderer=None):
#        obj = None #self.obj_for_value(value)
#        css_id = attrs.get('id', 'id_image_x')
#        related_url = None
#        change_url = ''
#        if value:
#            try:
#                file_obj = FilerFile.objects.get(pk=value)
#                related_url = file_obj.logical_folder.get_admin_directory_listing_url_path()
#                change_url = file_obj.get_admin_change_url()
#            except Exception as e:
#                raise
#        if not related_url:
#            related_url = reverse('admin:filer-directory_listing-last')
#        params = {'_to_field': 'id', '_popup': '1'} #self.url_parameters()
#        params['_pick'] = 'file'
#        if params:
#            lookup_url = '?' + urlencode(sorted(params.items()))
#        else:
#            lookup_url = ''
#        if 'class' not in attrs:
#            # The JavaScript looks for this hook.
#            attrs['class'] = 'vForeignKeyRawIdAdminField'
#        # rendering the super for ForeignKeyRawIdWidget on purpose here because
#        # we only need the input and none of the other stuff that
#        # ForeignKeyRawIdWidget adds
#        hidden_input = None #super(ForeignKeyRawIdWidget, self).render(name, value, attrs)  # grandparent super
#        context = {
#            'hidden_input': hidden_input,
#            'lookup_url': f'{related_url}{lookup_url}',
#            'change_url': change_url,
#            'object': obj,
#            'lookup_name': name,
#            'id': css_id,
#            'admin_icon_delete': ('admin/img/icon-deletelink.svg'),
#        }
#        html = render_to_string('admin/filer/widgets/admin_file.html', context)
#        return mark_safe(html)
#
# class FilerFileFormField(forms.ModelChoiceField):
#    widget = FilerFileWidget
#
#    def __init__(self, queryset, *args, **kwargs):
#        self.rel = None #rel
#        self.queryset = queryset
#        self.to_field_name = "id" #to_field_name
#        self.max_value = None
#        self.min_value = None
#        kwargs.pop('widget', None)
#        super().__init__(queryset, widget=self.widget(self.rel, site), *args, **kwargs)
#
#    def widget_attrs(self, widget):
#        widget.required = self.required
#        return {}


class PrettyJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, indent, sort_keys, **kwargs):
        super().__init__(*args, indent=4, sort_keys=True, **kwargs)


class FilerModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.logical_path[-1]}/{obj}"


class ReportJSONFormField(forms.JSONField):
    widget = UnfoldAdminTextareaWidget

    def to_python(self, value):
        if value in self.empty_values:
            return None
        if isinstance(value, str):
            try:
                return jsonc.loads(value)
            except Exception as ex:
                raise ValidationError("Enter valid JSON.") from ex
        return super().to_python(value)

    def prepare_value(self, value):
        if value in self.empty_values:
            return ""

        parsed = value
        if isinstance(value, str):
            try:
                parsed = jsonc.loads(value)
            except Exception:
                return value

        try:
            return json.dumps(parsed, indent=2, sort_keys=True)
        except (TypeError, ValueError):
            return str(value)


# Generic helper to construct Unfold-styled form fields for report inputs
def _make_report_input_field(field: ReportInputField):
    """Return a django form Field instance for a ReportInputField-like object.

    This centralizes the widget mapping so migrating other forms is simpler.
    """
    name = field.name
    desc = field.description
    ft = field.field_type

    if ft == "int":
        return forms.IntegerField(
            required=False, label=name, help_text=desc, widget=UnfoldAdminDecimalFieldWidget()
        )
    if ft == "float":
        return forms.FloatField(
            required=False, label=name, help_text=desc, widget=UnfoldAdminDecimalFieldWidget()
        )
    if ft == "date":
        return forms.DateField(
            required=False, label=name, help_text=desc, widget=UnfoldAdminDateWidget()
        )
    if ft == "bool":
        return forms.BooleanField(
            required=False, label=name, help_text=desc, widget=UnfoldBooleanSwitchWidget()
        )
    if ft == "json":
        f = ReportJSONFormField(
            required=False,
            label=name,
            help_text=desc,
            widget=UnfoldAdminTextareaWidget(),
        )
        f.widget.attrs.update({"style": "width: 750px; min-height: 280px;"})
        return f
    if ft == "file":
        f = FilerModelChoiceField(
            required=False,
            queryset=FilerFile.objects,
            label=name,
            help_text=desc,
            widget=UnfoldAdminSelect2Widget(),
        )
        f.widget.attrs.update({"style": "min-width: 750px;"})
        return f
    if ft == "buildingIds":
        buildingList = Building.objects.filter(active=True).order_by("name")
        buildingMapping = [(b.id, b.name) for b in buildingList]
        return forms.ChoiceField(
            label=name,
            required=False,
            choices=buildingMapping,
            widget=UnfoldAdminSelect2Widget(),
            help_text=desc,
        )
    if ft == "enum_monthly_weights":
        return forms.ChoiceField(
            required=False,
            label=name,
            help_text=desc,
            widget=UnfoldAdminSelectWidget(),
            choices=report.nk.cost_config.build_monthly_weights_choices(),
        )
    if ft == "enum_section_weights":
        return forms.ChoiceField(
            required=False,
            label=name,
            help_text=desc,
            widget=UnfoldAdminSelectWidget(),
            choices=report.nk.cost_config.build_section_weights_choices(),
        )
    if ft == "enum_object_weights":
        return forms.ChoiceField(
            required=False,
            label=name,
            help_text=desc,
            widget=UnfoldAdminSelectWidget(),
            choices=report.nk.cost_config.build_object_weights_choices(),
        )
    if ft == "enum_vewa_category":
        return forms.ChoiceField(
            required=False,
            label=name,
            help_text=desc,
            widget=UnfoldAdminSelectWidget(),
            choices=report.nk.cost_config.build_vewa_category_choices(),
        )

    # default
    return forms.CharField(
        required=False, label=name, help_text=desc, widget=UnfoldAdminTextInputWidget()
    )

    class Media:
        js = ("geno/js/select2-focus.js",)


class ReportConfigForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.report = kwargs.pop("report")
        super().__init__(*args, **kwargs)
        if not self.report:
            return
        for item in ReportItem.objects.filter(report_configuration=self.report):
            for field in ReportInputField.objects.filter(item_configuration=item).filter(
                active=True
            ):
                field_name = f"report_input_{field.id}"
                self.fields[field_name] = _make_report_input_field(field)
