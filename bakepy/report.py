import logging
import base64
import os
import warnings

import copy as copy_lib

from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

from bs4 import BeautifulSoup

from .html import Body, Container, Row, Column
from .utils import as_list, get_filename, get_valid_list_idx, limit_list_insert_idx, check_is_url, get_image_data, Working_Directory
from .recipes import get_html, get_recipes, get_recipe_info
from .rendering import get_renderers, get_renderer_info


@dataclass
class Report:
    """
    The report class is a collection of containers. A custom interface for a HTML Body.
    """
    name : str = "BakePy_Report"

    main_stylesheet: str = """<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-iYQeCzEYFbKjA/T2uDLTpkwGzCiq6soy8tYaI1GyVh/UjpbCx/TYkiZhlZB6+fzT" crossorigin="anonymous">
                              <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.2/dist/katex.min.css" integrity="sha384-bYdxxUwYipFNohQlHt0bjN/LCpueqWz13HufFEV1SUatKs1cm4L6fFgCi1jT643X" crossorigin="anonymous">"""
    stylesheets: Any = field(default_factory=list)

    cont_default_styles: Any = field(default_factory=list)
    cont_default_classes: Any = field(default_factory=lambda:["my-5"])
    row_default_styles: Any = field(default_factory=list)
    row_default_classes: Any = field(default_factory=lambda:["justify-content-center mb-5 gx-5"])
    col_default_styles: Any = field(default_factory=list)
    col_default_classes: Any = field(default_factory=list)

    current_container : Any = None
    current_container_name : str = None
    current_row : Any = None
    current_row_idx : Any = None
    current_col : Any = None
    current_col_idx : Any = None

    containers: Any = field(default_factory=dict)
        
    body : Body = None

    def __post_init__(self):
        self.body = Body(name=self.name, main_stylesheet=self.main_stylesheet, stylesheets=self.stylesheets)

    def _kwargs_defaults(self, kwargs, key, val):
        """
        Modify a kwargs dictionary to add a default value.
        """
        kwargs = kwargs.copy()

        if key in kwargs:
            kwargs[key] = as_list(val) + as_list(kwargs[key])
        else:
            kwargs[key] = val
        return kwargs

    def add_container(self, name = "default_container", overwrite = False, **kwargs):
        """
        Create a new container.
        
        Parameters
        ----------
        name : str, default = "default_container"
            The name of the new container.
        overwrite : bool, default = False
            If overriding an existing container.

        Notes
        ----------
            The report's current container will be set to the newly created container.
        """
        
        if name in self.containers.keys() and not overwrite:
            raise Exception(f"Container {name} already exists. If you wish to overwrite it, set overwrite=True.")
            
        idx = len(self.body.elements)

        if name in self.containers.keys() and overwrite:
            idx = self.body.elements.index(self.current_container)

        kwargs = self._kwargs_defaults(kwargs, "classes", self.cont_default_classes)
        kwargs = self._kwargs_defaults(kwargs, "styles", self.cont_default_styles)

        new_cont = Container(name = name, **kwargs)

        self.containers[name] = new_cont

        self.body.add_element(new_cont, pos=idx, replace=overwrite)

        self.set_current_container(name)

    def remove_container(self, name = None):
        """
        Remove a container.
        
        Parameters
        ----------
        name : str, default = None
            The name of the container to remove. If None, it will be treated as the current_container.

        Returns
        ----------
        e : Container
            The removed container object.
        e_o : dict
            The parse options associated to the removed object.
        """
        if len(self.containers) == 0:
            raise Exception("No containers to remove.")

        if name is None:
            name = self.current_container_name

        if name not in self.containers.keys():
            raise Exception(f"Container {name} does not exist.")
        
        del self.containers[name]
        e, e_o = self.body.pop_element(self.body.elements.index(self.current_container))

        if name == self.current_container_name:
            self.current_container = None

        self._verify_current_pos()
        return e, e_o

    def _verify_current_pos(self):
        """
        Verify that the current position is valid.

        Notes
        ----------
            The current position is made up of the current_container, current_row and current_col.
            If any of those is invalid, this function sets the current position to the last element of the smallest valid section.
            For example, if the container and row are valid but the column is not, the row is the smallest valid section so the position
            would be set to the last column of the current row.
        """
        #Verify the container
        if self.current_container is None:
            self.current_row = None
            self.current_row_idx = None
            self.current_col = None
            self.current_col_idx = None
            if len(self.containers) == 0:
                self.current_container_name = None
                #Nothing left to do
                return
            else:
                self.current_container_name = list(self.containers)[-1]
                self.current_container = self.containers[self.current_container_name]
                logging.info(f"Set current container to {self.current_container_name}.")
        #Verify the current row
        if self.current_row is None or not any([self.current_row is x for x in self.current_container.elements]):
            self.current_col = None
            self.current_col_idx = None
            c_items = len(self.current_container.elements)
            if c_items == 0:
                self.current_row = None
                self.current_row_idx = None
                logging.info(f"Container {self.current_container_name} is empty.")
                return
            else:
                self.current_row_idx = c_items-1
                self.current_row = self.current_container.elements[self.current_row_idx]
                logging.info(f"Set current row to {self.current_row_idx}.")
        #Verify the current column
        if self.current_col is None or not any([self.current_col is x for x in self.current_row.elements]):
            c_items = len(self.current_row.elements)
            if c_items == 0:
                self.current_col = None
                self.current_col_idx = None
                logging.info(f"Row {self.current_row_idx} is empty.")
            else:
                self.current_col_idx = c_items-1
                self.current_col = self.current_row.elements[self.current_col_idx]
                logging.info(f"Set current col to {self.current_row_idx}.")

    def get_container(self, name, **kwargs):
        """
        Gets a container object.

        Parameters
        ----------
        name : str
            The name of the container.

        Returns
        ----------
        cont : Container
            A Container object.
        """
        if name not in self.containers.keys():
            self.add_container(name, **kwargs)
        return self.containers[name]

    def get_current_container(self):
        """
        Gets the current container object.

        Returns
        ----------
        cont : Container
            A Container object.

        Notes
        ----------
            If there is no current container, a new one is created.
        """
        if self.current_container is None:
            self.add_container()
        return self.current_container

    def _get_container_from_name_arg(self, container_name):
        """
        Gets a container object. Function meant to be used to sanitize user input.

        Parameters
        ----------
        container_name : str
            The name of the container. If None, returns the current container.

        Returns
        ----------
        cont : Container
            A Container object.
        """
        if container_name is None:
            return self.get_current_container()
        else:
            cont = self.get_container(container_name)
            self.set_current_container(container_name)
            return cont

    def set_current_container(self, name):
        """
        Set the current container.

        Parameters
        ----------
        container_name : str
            The name of the container.
        """
        if name not in self.containers.keys():
            raise Exception(f"Container {name} does not exist.")
        
        self.current_container = self.containers[name]
        self.current_container_name = name
        self.current_row = None
        self.current_row_idx = None
        self.current_col = None
        self.current_col_idx = None
        self._verify_current_pos()
        
    def add_row(self, row_idx = None, container_name = None, overwrite = False,  **kwargs):
        """
        Create a new row.
        
        Parameters
        ----------
        row_idx : int, default = None
            The index of the container to insert the row at. If None, inserts it at the end.
        container_name : str, default = None
            The name of the container to use. If None, uses the default container.
        overwrite : bool, default = False
            If overriding an existing row.

        Notes
        ----------
            The report's current row will be set to the newly created row.
        """
        container = self._get_container_from_name_arg(container_name)
        row_idx = limit_list_insert_idx(row_idx, container.elements)

        kwargs = self._kwargs_defaults(kwargs, "classes", self.row_default_classes)
        kwargs = self._kwargs_defaults(kwargs, "styles", self.row_default_styles)

        container.add_element(Row(**kwargs), pos=row_idx, replace=overwrite)
        self.set_current_row(row_idx)

    def remove_row(self, row_idx = None, container_name = None):
        """
        Remove a row.
        
        Parameters
        ----------
        row_idx : int, default = None
            The index of the row to remove. If None, it will be treated as the current_row.
        container_name : str, default = None
            The name of the container to remove at. If None, it will be treated as the current_container.
    
        Returns
        ----------
        e : Row
            The removed row object.
        e_o : dict
            The parse options associated to the removed object.
        """
        container = self._get_container_from_name_arg(container_name)
        
        if row_idx is None:
            row_idx = self.current_row_idx
        if row_idx is None:
            raise Exception("No row to remove.")
        
        row_idx = get_valid_list_idx(row_idx, container.elements, container_name)
        e, e_o = container.pop_element(row_idx)

        if row_idx == self.current_row_idx:
            self.current_row = None
        
        if self.current_row_idx > row_idx:
            self.current_row_idx = self.current_row_idx - 1
            self.current_row = self.current_container.elements[self.current_row_idx]

        self._verify_current_pos()

        return e, e_o

    def get_row(self, row_idx, container_name = None):
        """
        Gets a row object.

        Parameters
        ----------
        row_idx : int
            The index of the row.
        container_name : str, default = None
            The name of the container. If None, uses the current_container.

        Returns
        ----------
        row : Row
            A Row object.
        """
        container = self._get_container_from_name_arg(container_name)
        row_idx = get_valid_list_idx(row_idx, container.elements, container_name)
        return container.elements[row_idx]

    def get_current_row(self):
        """
        Gets the current row object.

        Returns
        ----------
        row : Row
            A Row object.

        Notes
        ----------
            If there is no current row, a new one is created.
        """
        if self.current_row is None:
            self.add_row()
        return self.current_row

    def _get_row_from_idx_arg(self, row_idx = None, container_name = None):
        """
        Gets a row object. Function meant to be used to sanitize user input.

        Parameters
        ----------
        row_idx : int, default = None
            The index of the row. If None, returns the current row.
        container_name : str, default = None
            The name of the container. If None, uses the current container.

        Returns
        ----------
        row : Row
            A Row object.
        """
        container = self._get_container_from_name_arg(container_name)

        if row_idx is None:
            return self.get_current_row()
        else:
            r = self.get_row(row_idx)
            self.set_current_row(row_idx)
            return r

    def set_current_row(self, row_idx, container_name = None):
        """
        Set the current row.

        Parameters
        ----------
        row_idx : int
            The index of the row.
        container_name : str, default = None
            The name of the container. If None, uses the current container.
        """
        container = self._get_container_from_name_arg(container_name)
        row_idx = get_valid_list_idx(row_idx, container.elements, container_name)

        self.current_row_idx = row_idx
        self.current_row = container.elements[row_idx]
        self.current_col = None
        self.current_col_idx = None
        self._verify_current_pos()

    def add_col(self, col_idx = None, row_idx = None, container_name = None, overwrite = False, **kwargs):
        """
        Create a new column.
        
        Parameters
        ----------
        col_idx : int, default = None
            The index of the row to insert the column at. If None, inserts it at the end.
        row_idx : int, default = None
            The index of the row to use. If None, uses the current row.
        container_name : str, default = None
            The name of the container to use. If None, uses the default container.
        overwrite : bool, default = False
            If overriding an existing col.

        Notes
        ----------
            The report's current column will be set to the newly created column.
        """
        row = self._get_row_from_idx_arg(row_idx, container_name)
        col_idx = limit_list_insert_idx(col_idx, row.elements, overwrite)

        kwargs = self._kwargs_defaults(kwargs, "classes", self.col_default_classes)
        kwargs = self._kwargs_defaults(kwargs, "styles", self.col_default_styles)

        row.add_element(Column(**kwargs), pos=col_idx, replace=overwrite)
        self.set_current_col(col_idx)
        
    def remove_col(self, col_idx = None, row_idx = None, container_name = None):
        """
        Remove a column.
        
        Parameters
        ----------
        col_idx : int, default = None
            The index of the column to remove. If None, it will be treated as the current_col.
        row_idx : int, default = None
            The index of the row to remove at. If None, it will be treated as the current_row.
        container_name : str, default = None
            The name of the container to remove at. If None, it will be treated as the current_container.
    
        Returns
        ----------
        e : Row
            The removed column object.
        e_o : dict
            The parse options associated to the removed object.
        """
        row = self._get_row_from_idx_arg(row_idx, container_name)
        
        if col_idx is None:
            col_idx = self.current_col_idx
        if col_idx is None:
            raise Exception("No col to remove.")
        
        col_idx = get_valid_list_idx(col_idx, row.elements, f"Row_{row_idx}")
        e, e_o = row.pop_element(col_idx)

        if col_idx == self.current_col_idx:
            self.current_row = None
        
        if self.current_col_idx > col_idx:
            self.current_col_idx = self.current_col_idx - 1
            self.current_col = self.current_container.elements[self.current_col_idx]

        self._verify_current_pos()

        return e, e_o

    def get_col(self, col_idx, row_idx = None, container_name = None):
        """
        Gets a column object.

        Parameters
        ----------
        col_idx : int
            The index of the column.
        row_idx : int, default = None
            The index of the row. If None, uses the current_row.
        container_name : str, default = None
            The name of the container. If None, uses the current_container.

        Returns
        ----------
        col : Column
            A Column object.
        """
        row = self._get_row_from_idx_arg(row_idx, container_name)
        col_idx = get_valid_list_idx(col_idx, row.elements, f"Row_{row_idx}")
        return row.elements[col_idx]

    def get_current_col(self):
        """
        Gets the current column object.

        Returns
        ----------
        col : Column
            A Column object.

        Notes
        ----------
            If there is no current column, a new one is created.
        """
        if self.current_col is None:
            self.add_col()
        return self.current_col

    def _get_col_from_idx_arg(self, col_idx = None, row_idx = None, container_name = None):
        """
        Gets a column object. Function meant to be used to sanitize user input.

        Parameters
        ----------
        col_idx : int, default = None
            The index of the column. If None, returns the current column.
        row_idx : int, default = None
            The index of the row. If None, uses the current row.
        container_name : str, default = None
            The name of the container. If None, uses the current container.

        Returns
        ----------
        col: Column
            A Column object.
        """
        row = self._get_row_from_idx_arg(row_idx, container_name)

        if col_idx is None:
            return self.get_current_col()
        else:
            r = self.get_col(col_idx)
            self.set_current_col(col_idx)
            return r

    def set_current_col(self, col_idx, row_idx = None, container_name = None):
        """
        Set the current column.

        Parameters
        ----------
        col_idx : int
            The index of the column.
        row_idx : int, default = None
            The index of the row. If None, uses the current row.
        container_name : str, default = None
            The name of the container. If None, uses the current container.
        """
        row = self._get_row_from_idx_arg(row_idx, container_name)
        col_idx = get_valid_list_idx(col_idx, row.elements, f"Row_{row_idx}")

        self.current_col_idx = col_idx
        self.current_col = row.elements[col_idx]
        self._verify_current_pos()    

    def set_container_cls(self, vals, container_name = None, overwrite = False):
        """
        Set a container's classes.

        Parameters
        ----------
        vals : list/str
            The classes to add.
        container_name : str, default = None
            The name of the container. If None, uses the current container.
        overwrite : bool, default = False
            Set to true if overwriting the current classes.
        """
        e = self._get_container_from_name_arg(container_name = container_name)
        e.add_cls(vals, overwrite)
    
    def set_container_sty(self, vals, container_name = None, overwrite = False):
        """
        Set a container's styles.

        Parameters
        ----------
        vals : list/str
            The styles to add.
        container_name : str, default = None
            The name of the container. If None, uses the current container.
        overwrite : bool, default = False
            Set to true if overwriting the current styles.
        """
        e = self._get_container_from_name_arg(container_name = container_name)
        e.add_sty(vals, overwrite)

    def set_row_cls(self, vals, row_idx = None, container_name = None, overwrite = False):
        """
        Set a row's classes.

        Parameters
        ----------
        vals : list/str
            The classes to add.
        row_idx : int, default = None
            The index of the row. If None, uses the current row.
        container_name : str, default = None
            The name of the container. If None, uses the current container.
        overwrite : bool, default = False
            Set to true if overwriting the current classes.
        """
        e = self._get_row_from_idx_arg(row_idx = row_idx, container_name = container_name)
        e.add_cls(vals, overwrite)
    
    def set_row_sty(self, vals, row_idx = None, container_name = None, overwrite = False):
        """
        Set a row's styles.

        Parameters
        ----------
        vals : list/str
            The styles to add.
        row_idx : int, default = None
            The index of the row. If None, uses the current row.
        container_name : str, default = None
            The name of the container. If None, uses the current container.
        overwrite : bool, default = False
            Set to true if overwriting the current styles.
        """
        e = self._get_row_from_idx_arg(row_idx = row_idx, container_name = container_name)
        e.add_sty(vals, overwrite)

    def set_col_cls(self, vals, col_idx = None, row_idx = None, container_name = None, overwrite = False):
        """
        Set a column's classes.

        Parameters
        ----------
        vals : list/str
            The classes to add.
        col_idx : int, default = None
            The index of the column. If None, uses the current column.
        row_idx : int, default = None
            The index of the row. If None, uses the current row.
        container_name : str, default = None
            The name of the container. If None, uses the current container.
        overwrite : bool, default = False
            Set to true if overwriting the current classes.
        """
        e = self._get_col_from_idx_arg(col_idx = col_idx, row_idx = row_idx, container_name = container_name)
        e.add_cls(vals, overwrite)

    def set_col_sty(self, vals, col_idx = None, row_idx = None, container_name = None, overwrite = False):
        """
        Set a column's styles.

        Parameters
        ----------
        vals : list/str
            The styles to add.
        col_idx : int, default = None
            The index of the column. If None, uses the current column.
        row_idx : int, default = None
            The index of the row. If None, uses the current row.
        container_name : str, default = None
            The name of the container. If None, uses the current container.
        overwrite : bool, default = False
            Set to true if overwriting the current styles.
        """
        e = self._get_col_from_idx_arg(col_idx = col_idx, row_idx = row_idx, container_name = container_name)
        e.add_sty(vals, overwrite)

    def add(self,
            elements,
            container_name = None,
            row_idx = None,
            col_idx = None,
            new_row = True,
            new_col = True,
            size = None,
            copy = False,
            overwrite = False,
            **other_args):
        """
        Add content to the report.

        Parameters
        ----------
        elements : list/Object
            The elements to add.
        container_name : str, default = None
            The name of the container to insert at. If None, uses the current container.
        row_idx : int, default = None
            The index of the row to insert at. If None, uses the current row.
        col_idx : int, default = None
            The index of the column to insert at. If None, inserts at the end of the row.
        new_row : bool, default = True
            If True, the elements will be added in a new row.
        new_col : bool, default = True
            If True, the elements will be added in a new column. Takes precedence over new_row.
        size : int, default = None
            The width of the column to insert.
        copy : bool, default = False
            If True, the elements will be copied before inserting.
        overwrite : bool, default = False
            Set to true if overwriting the item in the specified position.
        """

        elements = as_list(elements)
        if new_col and new_row and not overwrite:
            self.add_row(row_idx = row_idx, container_name = container_name, overwrite = False)
        if new_col and not overwrite:
            self.add_col(col_idx = col_idx, row_idx = row_idx, container_name = container_name, overwrite = False)
        
        if overwrite:
            #First verify that the column we want to overwrite actually exists.
            self._get_col_from_idx_arg(col_idx = col_idx, row_idx = row_idx, container_name = container_name)
            self.add_col(col_idx = col_idx, row_idx = row_idx, container_name = container_name, overwrite = True)

        col = self._get_col_from_idx_arg(col_idx = col_idx, row_idx = row_idx, container_name = container_name)
        if size is not None:
            col.size = size
        
        for e in elements:
            if copy:
                col.add_element(copy_lib.copy(e), **other_args)
            else:
                col.add_element(e, **other_args)
        
    def recipe(self,
               type,
               *args,
               container_name = None,
               row_idx = None,
               col_idx = None,
               new_row = True,
               new_col = True,
               size = None,
               copy = False,
               overwrite = False,
               **kwargs):
        """
        Add specially formatted content to the report.

        Parameters
        ----------
        type : str
            The type of content to insert.
        container_name : str, default = None
            The name of the container to insert at. If None, uses the current container.
        row_idx : int, default = None
            The index of the row to insert at. If None, uses the current row.
        col_idx : int, default = None
            The index of the column to insert at. If None, inserts at the end of the row.
        new_row : bool, default = True
            If True, the elements will be added in a new row.
        new_col : bool, default = True
            If True, the elements will be added in a new column.
        size : int, default = None
            The width of the column to insert.
        copy : bool, default = False
            If True, the elements will be copied before inserting.
        overwrite : bool, default = False
            Set to true if overwriting the item in the specified position.
        """

        self.add(get_html(type, *args, **kwargs), container_name, row_idx, col_idx, new_row, new_col, size, copy, overwrite)

    @staticmethod
    def get_recipes():
        """
        Get all available recipes.
        """
        return get_recipes()

    @staticmethod
    def get_recipe_info(recipe):
        """
        Get information about a recipe.

        Parameters
        ----------
        recipe: str
            The name of a recipe.
        """
        return get_recipe_info(recipe)

    @staticmethod
    def get_renderers():
        """
        Get all available renderers.
        """
        return get_renderers()

    @staticmethod
    def get_renderer_info(recipe, verbose = False):
        """
        Get information about the renderer associated to an element.

        Parameters
        ----------
        element: object
            An object.
        verbose: bool, default = False
            If True, prints the process of finding the renderer.
        """
        return get_renderer_info(recipe, verbose)

    def save_html(self, filename = None, embed_images=True, embed_links=True):
        """
        Save the report to an HTML file.

        Parameters
        ----------
        filename : str, default = None
            The path to save at. If None, uses the report name.
        embed_images : bool, default = True
            If True, embeds any linked images as base64.
        embed_links : bool, default = True
            If True, embeds any linked styles.
        """

        if filename is None:
            output_dir = Path().cwd().absolute()
        else:
            output_dir = Path(filename).parent.absolute()

        with Working_Directory(output_dir) as wd:

            html = self.body.to_html()
            soup = BeautifulSoup(html, "html.parser")

            #Embed images as base64
            if embed_images:
                for img in soup.find_all('img'):
                    img_src = img.attrs['src']
                    #If image is already embedded, skip.
                    if img_src.startswith('data:'):
                        continue
                    img_type, img_data = get_image_data(img_src)                   
                    img.attrs['src'] = f"data:{img_type};base64,{str(base64.b64encode(img_data),'utf-8')}"
            #Embed links (stylesheets) using bs4
            #TODO

            #Save the file
            name = self.name
            
            if name == "":
                name = id(self)
                
            if filename is None:
                filename = name
                
            filename = get_filename(filename, "html")

            with open(filename, 'w') as f:
                f.write(soup.prettify())

    # def save_pdf(self, filename = None):
    #     """
    #     Save the report to an PDF file.

    #     Parameters
    #     ----------
    #     filename : str, default = None
    #         The path to save at. If None, uses the report name.
    #     """
    #     import weasyprint

    #     name = self.name
        
    #     if name == "":
    #         name = id(self)
            
    #     if filename is None:
    #         filename = name
            
    #     filename = get_filename(filename, "pdf")
            
    #     weasyprint.HTML(string=self.save_html(embed_images=True, embed_links=True)).write_pdf(filename)
