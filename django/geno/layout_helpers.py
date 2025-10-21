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
        self.css_class = css_class or ''

    def render(self, form, context, template_pack=None, **kwargs):
        """Render the separator component."""
        template_context = {
            'vertical': self.vertical,
            'class': self.css_class,
        }
        return render_to_string(self.template, template_context)
