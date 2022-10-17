from abc import ABC
from dataclasses import dataclass, field
from typing import Any
from .utils import as_list

class HTMLElement(ABC):
    
    def add_element(self, element, pos = None, replace = False, **other_args):
        if pos is None:
            pos = len(self.elements)
        if replace:
            if pos >= len(self.elements):
                raise Exception(f"Cannot replace element at position {pos}.")
            self.pop_element(pos)
            self.elements.insert(pos, element)
            self.parse_options.insert(pos, other_args)
        else:
            self.elements.insert(pos, element)
            self.parse_options.insert(pos, other_args)

    def pop_element(self, pos = None):
        if pos is None or pos >= len(self.elements):
            pos = len(self.elements)-1
        try:
            return self.elements.pop(pos), self.parse_options.pop(pos)
        except:
            return None, None
    
    def get_head(self):
        cls_str = self.str_cls()
        style_str = self.str_sty()
        if len(cls_str) > 0:
            cls_str = f""" class="{cls_str}" """
        if len(style_str) > 0:
            style_str = f""" style="{style_str}" """
        return f"""<div{cls_str}{style_str}>"""
    
    def get_tail(self):
        return """</div>"""
    
    def to_html(self): 
        return self.get_head() +'\n'.join([self._get_html_element(x, **o) for (x, o) in zip(self.elements, self.parse_options)])+ self.get_tail()
    
    def str_main_cls(self):
        return self.main_class
    
    def add_cls(self, to_add, overwrite = False):
        to_add = as_list(to_add)
        if overwrite:
            self.classes = to_add
        else:
            self.classes = self.classes + to_add
        
    def add_sty(self, to_add, overwrite = False):
        to_add = as_list(to_add)
        if overwrite:
            self.styles = to_add
        else:
            self.styles = self.styles + to_add

    def get_cls(self):
        return [self.str_main_cls()] + self.classes
    
    def str_cls(self):
        return " ".join(self.get_cls())
    
    def str_sty(self):
        return " ".join(self.styles)
    
    def _get_html_element(self, element, **options):
        """
        Mapping for different types of objects from the parsing submodule.
        """
        from .rendering import get_html
        return get_html(element, **options)

@dataclass
class Body(HTMLElement):
    """
    An HTML5 body with Bootstrap 5 support.
    """
    name : str = ""
    elements: Any = field(default_factory=list)
    parse_options: Any = field(default_factory=list)
    main_stylesheet: str = """<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-iYQeCzEYFbKjA/T2uDLTpkwGzCiq6soy8tYaI1GyVh/UjpbCx/TYkiZhlZB6+fzT" crossorigin="anonymous">"""
    stylesheets: Any = field(default_factory=list)
        
    def get_head(self):
        return f"""<!doctype html>
                    <html lang="en">
                      <head>
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                        <title>{self.name}</title>
                        {self.main_stylesheet}
                        {" ".join(self.stylesheets)}
                      </head>

                      <body>"""
    def get_tail(self):
        return "</body></html>"
            
@dataclass
class Container(HTMLElement):
    """
    A container has a collection of elements (rows/columns/containers).
    """
    name : str = ""
    elements: Any = field(default_factory=list)
    parse_options: Any = field(default_factory=list)
    classes: Any = field(default_factory=list)
    styles: Any = field(default_factory=list)
    main_class: str = "container"

@dataclass
class Row(HTMLElement):
    """
    A Bootstrap 5 row element.
    """
    name : str = ""
    elements: Any = field(default_factory=list)
    parse_options: Any = field(default_factory=list)
    classes: Any = field(default_factory=list)
    styles: Any = field(default_factory=list)
    main_class: str = "row"

@dataclass
class Column(HTMLElement):
    """
    A Bootstrap 5 column element.
    """
    name : str = ""
    elements: Any = field(default_factory=list)
    parse_options: Any = field(default_factory=list)
    classes: Any = field(default_factory=list)
    styles: Any = field(default_factory=list)
    size: Any = None
    main_class: str = "col"
        
    def str_main_cls(self):
        if self.size is not None:
            return f"col-{self.size}"
        return "col"