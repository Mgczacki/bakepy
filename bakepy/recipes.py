SPECIAL_FORMATS_DICT = dict()

#Decorator to register an HTML rendering function
def register_format(f_str):
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

@register_format("separator")
def _get_separator(classes = ["py-4"], styling = [], visible = True):
    
    if not visible:
        styling = styling + ["display:none;"]

    cls_str = ""
    if len(classes) > 0:
        cls_str = f""" class="{" ".join(classes)}" """
    style_str = ""
    if len(styling) > 0:
        style_str = f""" style="{" ".join(styling)}" """
        
    return f"""<hr{cls_str}{style_str}/>"""
    
@register_format("markdown")
def _get_markdown(text, classes = [], styling = [], latex=False):
    import markdown
    import mdtex2html

    if latex:
        html = mdtex2html.convert(text)
    else:
       html = markdown.markdown(text)
            
    cls_str = ""
    if len(classes) > 0:
        cls_str = f""" class="{" ".join(classes)}" """
    style_str = ""
    if len(styling) > 0:
        style_str = f""" style="{" ".join(styling)}" """
    return f"""<div{cls_str}{style_str}>{html}</div>"""