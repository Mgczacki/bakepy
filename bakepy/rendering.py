import warnings
import os
import base64

from pathlib import Path

from bs4 import BeautifulSoup

from .html import HTMLElement
from .utils import get_image_data

RENDER_FUNCTIONS_DICT = dict()

#Decorator to register an HTML rendering function
def register_html_renderer(cls):
    """
    Decorator to register a function to render HTML from an object.

    Parameters
    ----------
    cls: type/class
        The type/class to assign for the rendering function.
    Example
    ----------
    @register_html_renderer(cls=int)
    def _get_int_html(element, **_options):
        return str(element)
    """
    def registration(f):
        RENDER_FUNCTIONS_DICT[cls] = f
        return f
    return registration

def get_render_function(element, verbose = False):
    """
    Obtains the associated function to render an object.
    """
    inheritance = type(element).__mro__
    #Tries to find a function for each type in the inheritance order of the object.
    for i in inheritance:
        if i in RENDER_FUNCTIONS_DICT:
            if verbose:
                print(f"Found a renderer for the type {i}.")
            return RENDER_FUNCTIONS_DICT[i]
        else:
            if verbose:
                print(f"Found no associated renderer for the type {i}.")
    if verbose:
        print(f"Found no associated renderer for the inheritance. Returning default rendering function.")
    return _default_html_conversion

def get_renderers():
    return RENDER_FUNCTIONS_DICT.keys()

def get_renderer_info(element, verbose = False):
    try:
        return help(get_render_function(element, verbose))
    except:
        raise Exception("The element has no valid associated renderer.")

def get_html(element, **options):
    """
    Renders an object to an HTML string.
    
    Parameters
    ----------
    element: Object
        The object to render.
    options: dict
        An optional dictionary containing keyword arguments to be used by the rendering functon.
    Returns
    ----------
    repr: str
        An HTML string.
    """
    return get_render_function(element)(element, **options)

@register_html_renderer(cls=object)
def _default_html_conversion(element, **_options):
    """
    A default rendering function for any unimplemented types. Returns the object's string representation.

    Parameters
    ----------
    element: Object
        The object to render.
    _options: dict
        Unused. Kept for compatibility with get_html()
    Returns
    ----------
    repr: str
        An HTML string.
    """
    warnings.warn(f"There is no implementation for getting the HTML code of a {type(element)}. Using its string representation.")
    return str(element)

@register_html_renderer(cls=str)
def _get_str_html(element, **_options):
    """
    Rendering function for the string type. Returns the same object.

    Parameters
    ----------
    element: Object
        The object to render.
    _options: dict
        Unused. Kept for compatibility with get_html()
    Returns
    ----------
    repr: str
        An HTML string.
    """
    return element

@register_html_renderer(cls=HTMLElement)
def _get_htmlelement_html(element, **_options):
    """
    Rendering function for HTMLElement objects. Calls the object's to_html() function.

    Parameters
    ----------
    element: Object
        The object to render.
    _options: dict
        Unused. Kept for compatibility with get_html()
    Returns
    ----------
    repr: str
        An HTML string.
    """
    return element.to_html()

#Conditional registration of function; only if matplotlib and pandas installed

try:
    from pandas import DataFrame

    @register_html_renderer(cls=DataFrame)
    def _get_pandas_html(df, caption = None, classes = ["table", "table-bordered"], justify = "left", index=True, **options):
        """
        Rendering function for pandas dataframes.

        Parameters
        ----------
        df: DataFrame
            The dataframe to render.
        caption: str, default = None
            The table's caption.
        classes: list, default = ["table", "table-bordered"]
            A list of classes to apply to the HTML table generated.
        justify: str, default="left"
            The justification for the table's text.
        index: bool, default=True
            If True, adds the index to the HTML render of the dataframe.
        Returns
        ----------
        repr: str
            An HTML string.
        """
        html = df.to_html(index=index, classes = classes, justify=justify, **options)
        if caption is not None:
            html = html.replace("</thead>", f"""</thead>\n  <caption class="text-center">{caption}</caption>""")
        return html

except:
    warnings.warn(f"Tried to register render function for pandas dataframes but it failed. Is the library installed?")

try:
    import matplotlib.pyplot as plt

    from matplotlib.artist import Artist
    from matplotlib.figure import Figure

    @register_html_renderer(cls=Artist)
    def _get_matplotlib_html(fig, caption = None, save_format="svg", embed = True, **options):
        """
        Rendering function for matplotlib figures.

        Parameters
        ----------
        fig: Figure
            The figure to render.
        caption: str, default = None
            The figure's caption.
        save_format: str, default="svg"
            The save format for the output image.
        embed: bool, default=True
            An option that allows the embedding of the image directly into the HTML document rather than in a separate file.
        Returns
        -------
        repr: str
            An HTML string.
        """
        if not isinstance(fig, Figure):
            try:
                fig = fig.figure
            except:
                raise Exception("The provided matplotlib object does not contain a Figure.")

        old_config = plt.rcParams['svg.fonttype']
        
        filename = f"BAKEPY_IMG_{id(fig)}.{save_format}"

        plt.rcParams['svg.fonttype'] = 'none'
        fig.savefig(filename, format=save_format, bbox_inches='tight', **options)
        
        if save_format == "svg":
            #Change the format of svg file to have max width/height
            with open(filename,'r+') as file:
                soup = BeautifulSoup(file, features="lxml-xml")
                for svg_f in soup.find_all('svg'):
                    svg_f.attrs["width"] = "100%"
                    svg_f.attrs["height"] = "100%"
                file.seek(0)
                file.write(str(soup))
                file.truncate()

        plt.rcParams['svg.fonttype'] = old_config
        
        str_caption = ""

        if caption is not None:
            str_caption = f"""<figcaption class="figure-caption text-center">{caption}</figcaption>"""

        if embed:
            img_type, img_data = get_image_data(filename)                   
            img_src = f"data:{img_type};base64,{str(base64.b64encode(img_data),'utf-8')}"
            try:
                os.remove(filename)
            except:
                warnings.warn(f"Could not delete file {filename}.") 
        else:
            img_src = filename

        return f"""<figure class="figure" style="width:100%;">
                    <img src="{img_src}" class="figure-img img-fluid">
                    {str_caption}
                </figure>"""

except:
    warnings.warn(f"Tried to register render function for matplotlib figures but it failed. Is the library installed?")