SPECIAL_FORMATS_DICT = dict()

#Decorator to register an HTML rendering function
def register_recipe(f_str):
    """
    Decorator to register a function that generates specially formatted HTML.
    Parameters
    ----------
    f_str: str
        The name of the format.
    Example
    ----------
    @register_format(f_str="greet")
    def _get_greeting(*args, **kwargs):
        return "<h1>Hello!</h1>"
    """
    def registration(f):
        SPECIAL_FORMATS_DICT[f_str] = f
        return f
    return registration

def get_html(format_type, *args, **kwargs):
    """
    Gets a specially formatted HTML string.
    Parameters
    ----------
    format_type: str
        The name of the format.
    Returns
    ----------
    repr: str
        An HTML string.
    """
    return SPECIAL_FORMATS_DICT[format_type](*args, **kwargs)

def get_recipes():
    return SPECIAL_FORMATS_DICT.keys()

def get_recipe_info(recipe):
    try:
        return help(SPECIAL_FORMATS_DICT[recipe])
    except:
        raise Exception(f"{recipe} is not registered as a BakePy Recipe.")

@register_recipe("separator")
def _get_separator(classes = ["py-4"], styling = []):
    """
    Generates a horizontal rule meant as a separator.

    Parameters
    ----------
    classes: list, default = ["py-4"]
        The classes to apply to the element.
    styling: list, default = []
        The styles to apply to the element.
    """
    
    cls_str = ""
    if len(classes) > 0:
        cls_str = f""" class="{" ".join(classes)}" """
    style_str = ""
    if len(styling) > 0:
        style_str = f""" style="{" ".join(styling)}" """
        
    return f"""<hr{cls_str}{style_str}/>"""

@register_recipe("img")
def _get_img(url, caption = None):
    """
    Adds an image from a path.

    Parameters
    ----------
    url: str
        The path (local or remote) to the image file.
    caption: str, default = None
        The caption for the image.
    """
    str_caption = ""

    if caption is not None:
        str_caption = f"""<figcaption class="figure-caption text-center">{caption}</figcaption>"""

    return f"""<figure class="figure" style="width:100%;">
                <img src="{url}" class="figure-img img-fluid">
                {str_caption}
            </figure>"""
    
@register_recipe("markdown")
def _get_markdown(text, classes = [], styling = [], latex=False):
    """
    Generates a block of text with interpreted as markdown.

    Parameters
    ----------
    text: str
        The string to parse as markdown.
    classes: list, default = []
        The classes to apply to the element.
    styling: list, default = []
        The styles to apply to the element.
    latex : bool, default = False
        If True, parsing for LaTeX is enabled.
    """
    import markdown
    from textwrap import dedent

    extensions = []
    extension_configs = {}

    if latex:
        extensions.append('markdown_katex')
        extension_configs['markdown_katex'] = {'no_inline_svg': False, 'insert_fonts_css': False}
        
    html = markdown.markdown(dedent(text), extensions=extensions, extension_configs=extension_configs)
        
    cls_str = ""
    if len(classes) > 0:
        cls_str = f""" class="{" ".join(classes)}" """
    style_str = ""
    if len(styling) > 0:
        style_str = f""" style="{" ".join(styling)}" """
    return f"""<div{cls_str}{style_str}>{html}</div>"""

@register_recipe(f_str="title")
def _get_title(text, level = 1, center = True):
    """
    Generates a title.

    Parameters
    ----------
    text: str
        The title contents.
    level: int, default = 1
        The Boostrap display-level.
    center: bool, default = True
        If True, centers the title horizontally.
    """
    c_str = f"""class = "display-{level}"""
    if center:
        c_str = c_str + " text-center"
    c_str = c_str + '"'
    return f"<h1 {c_str}> {text} </h1>"

@register_recipe(f_str="spacer")
def _get_spacer(level = 1):
    """
    Generates blank space.

    Parameters
    ----------
    level: int, default = 1
        The Boostrap margin size to apply to the spacer.
    """
    
    return f"""<div class="my-{level}" style="width: 100%;height: 1px;"></div>"""