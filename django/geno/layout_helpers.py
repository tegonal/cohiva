"""
Custom crispy forms layout objects for Unfold admin theme.

These provide reusable components that can be used in form layouts
while maintaining consistency with Unfold's design system.
"""

from crispy_forms.layout import LayoutObject
from django.template.loader import render_to_string


class UnfoldSeparator(LayoutObject):
    """
    Horizontal or vertical separator using Unfold's separator component.

    Args:
        vertical: If True, renders a vertical separator. Default: False (horizontal)
        css_class: Optional additional CSS classes

    Usage:
        from geno.layout_helpers import UnfoldSeparator

        Layout(
            Div('category', css_class='mb-4'),
            UnfoldSeparator(),  # Horizontal separator
            Div('date', css_class='mb-4'),
        )
    """

    template = "unfold/components/separator.html"

    def __init__(self, vertical=False, css_class=None):
        self.vertical = 1 if vertical else 0
        self.css_class = css_class or ""

    def render(self, form, context, template_pack=None, **kwargs):
        """Render the separator component."""
        template_context = {
            "vertical": self.vertical,
            "class": self.css_class,
        }
        return render_to_string(self.template, template_context)


class UnfoldSectionHeading(LayoutObject):
    """
    Section heading with Unfold's design system styling.

    Creates a consistent h3 heading for form sections with proper Unfold typography.

    Args:
        text: The heading text (can be a translation object)
        css_class: Optional additional CSS classes

    Usage:
        from geno.layout_helpers import UnfoldSectionHeading
        from django.utils.translation import gettext_lazy as _

        Layout(
            UnfoldSeparator(),
            UnfoldSectionHeading(_("Mitglieder-Filter")),
            Div('field1', css_class='mb-4'),
        )
    """

    template = "geno/layout/section_heading.html"

    def __init__(self, text, css_class=None):
        self.text = text
        self.css_class = css_class or ""

    def render(self, form, context, template_pack=None, **kwargs):
        """Render the section heading."""
        template_context = {
            "text": self.text,
            "css_class": self.css_class,
        }
        return render_to_string(self.template, template_context)


class ConditionalDiv(LayoutObject):
    """
    Conditional wrapper div with JavaScript-controlled visibility.

    Creates a div container with an ID for conditional field groups that can be
    shown/hidden via JavaScript based on other field selections.

    Args:
        div_id: HTML ID attribute for the div
        *fields: Field names or layout objects to include inside the div
        initial_display: CSS display value ('none', 'block', etc.). Default: 'none'
        css_class: Optional additional CSS classes

    Usage:
        from geno.layout_helpers import ConditionalDiv

        Layout(
            Div('base_dataset', css_class='mb-4'),
            ConditionalDiv(
                'member-filters',
                UnfoldSeparator(),
                UnfoldSectionHeading(_("Mitglieder-Filter")),
                Div('field1', css_class='mb-4'),
                initial_display='none',
            ),
        )
    """

    template = "geno/layout/conditional_div.html"

    def __init__(self, div_id, *fields, initial_display="none", css_class=None):
        self.div_id = div_id
        self.fields = list(fields)
        self.initial_display = initial_display
        self.css_class = css_class or ""

    def render(self, form, context, template_pack=None, **kwargs):
        """Render the conditional div and its contents."""
        from crispy_forms.utils import render_field

        # Render all child fields/layout objects
        fields_html = ""
        for field in self.fields:
            fields_html += render_field(
                field,
                form=form,
                context=context,
                template_pack=template_pack,
                **kwargs,
            )

        template_context = {
            "div_id": self.div_id,
            "fields_html": fields_html,
            "initial_display": self.initial_display,
            "css_class": self.css_class,
        }

        return render_to_string(self.template, template_context)


class CollapsibleSection(LayoutObject):
    """
    Collapsible section with a clickable header using Alpine.js.

    Creates a section that can be expanded/collapsed by clicking the header.
    Uses Unfold's design system and Alpine.js for interactivity.

    Args:
        heading: The heading text to display
        *fields: Field names or layout objects to include inside the section
        collapsed: If True, section starts collapsed. Default: True
        css_class: Optional additional CSS classes for the container

    Usage:
        from geno.layout_helpers import CollapsibleSection

        Layout(
            CollapsibleSection(
                _("Mitglieder-Attribute"),
                Div('field1', css_class='mb-4'),
                Div('field2', css_class='mb-4'),
                collapsed=True,
            ),
        )
    """

    template = "geno/layout/collapsible_section.html"

    def __init__(self, heading, *fields, collapsed=True, css_class=None):
        self.heading = heading
        self.fields = list(fields)
        self.collapsed = collapsed
        self.css_class = css_class or ""

    def render(self, form, context, template_pack=None, **kwargs):
        """Render the collapsible section."""
        from crispy_forms.utils import render_field

        # Render all child fields/layout objects
        fields_html = ""
        for field in self.fields:
            fields_html += render_field(
                field,
                form=form,
                context=context,
                template_pack=template_pack,
                **kwargs,
            )

        template_context = {
            "heading": self.heading,
            "fields_html": fields_html,
            "collapsed": self.collapsed,
            "css_class": self.css_class,
        }

        return render_to_string(self.template, template_context)
