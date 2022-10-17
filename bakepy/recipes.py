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
        f = SPECIAL_FORMATS_DICT[recipe]
    except:
        raise Exception(f"{recipe} is not registered as a BakePy Recipe.")

@register_recipe("separator")
def _get_separator(classes = ["py-4"], styling = []):
    
    cls_str = ""
    if len(classes) > 0:
        cls_str = f""" class="{" ".join(classes)}" """
    style_str = ""
    if len(styling) > 0:
        style_str = f""" style="{" ".join(styling)}" """
        
    return f"""<hr{cls_str}{style_str}/>"""
    
@register_recipe("markdown")
def _get_markdown(text, classes = [], styling = [], latex=False):

    import markdown
    extensions = []
    extension_configs = {}

    if latex:
        extensions.append('markdown_katex')
        extension_configs['markdown_katex'] = {'no_inline_svg': False, 'insert_fonts_css': False}
        
    html = markdown.markdown(text, extensions=extensions, extension_configs=extension_configs)
        
    cls_str = ""
    if len(classes) > 0:
        cls_str = f""" class="{" ".join(classes)}" """
    style_str = ""
    if len(styling) > 0:
        style_str = f""" style="{" ".join(styling)}" """
    return f"""<div{cls_str}{style_str}>{html}</div>"""

@register_recipe(f_str="title")
def _get_title(text, display_level = 1, heading_level = 1, center = True):
    
    c_str = f"""class = "display-{display_level}"""
    if center:
        c_str = c_str + " text-center"
    c_str = c_str + '"'
    return f"<h{heading_level} {c_str}> {text} </h{heading_level}>"

@register_recipe(f_str="spacer")
def _get_spacer(level = 1):
    
    return f"""<div class="my-{level}" style="width: 100%;height: 1px;"></div>"""