import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail import hooks
from wagtail.admin.rich_text.converters.html_to_contentstate import InlineStyleElementHandler


@hooks.register("register_rich_text_features")
def register_underline_feature(features):
    """
    Registering the `underline` feature, which uses the `Underline` Draft.js inline style type,
    and is stored as HTML with a `<span class="c-text-underline">` tag.
    """
    feature_name = "underline"
    type_ = "UNDERLINE"

    control = {
        "type": type_,
        "label": "⎁",
        "description": "Unterstrichen",
        # This isn’t even required – Draftail has predefined styles for UNDERLINE.
        # 'style': {'textDecoration': 'line-through'},
    }

    features.register_editor_plugin(
        "draftail", feature_name, draftail_features.InlineStyleFeature(control)
    )

    features.register_converter_rule(
        "contentstate",
        feature_name,
        {
            "from_database_format": {
                'span[class="c-text-underline"]': InlineStyleElementHandler(type_)
            },
            "to_database_format": {"style_map": {type_: 'span class="c-text-underline"'}},
        },
    )

    # (optional) Add the feature to the default features list to make it available
    # on rich text fields that do not specify an explicit 'features' list
    # features.default_features.append('underline')
