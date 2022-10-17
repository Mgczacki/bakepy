from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic, needs_local_scope)

from IPython.core.magic_arguments import (argument, magic_arguments,
    parse_argstring)

import markdown

def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    magics = BakeReportMagic(ipython)
    ipython.register_magics(magics)

def strparse(val):
    """
    Parse a string with support for spaces.
    """
    if val.startswith('"') and val.endswith('"'):
        #Using double-quotations
        return val.strip('"')
    if val.startswith("'") and val.endswith("'"):
        #Using single quotations
        return val.strip("'")
    return val

def boolparse(val):
    """
    Parse a Boolean value.
    """
    val = strparse(val).lower()
    if val in ["y", "yes", "true", "t"]:
        return True
    return False

def idparse(val):
    """
    Parse a string that can be used as a Python identifier.
    """
    val = strparse(val)
    if val.isidentifier():
        return val
    raise Exception("Invalid Report name. Must be a valid identifier name.")

@magics_class
class BakeReportMagic(Magics):
    #Add things to the report
    @needs_local_scope
    @magic_arguments()
    @argument('-R', '--report', default=None, type=idparse, help='The name of the report to use. If it does not exist, it is created. If None, uses the current active report. Must be a valid Python identifier name.')
    @argument('-C', '--container', default=None, type=strparse, help='The name of the container to use. If it does not exist, it is created.')
    @argument('-r', '--row', default=None, type=int, help='The row position to use. If none provided, uses the current row.')
    @argument('-c', '--col', default=None, type=int, help='The position to take in the row. If none provided, inserts at the end of the current row.')
    @argument('-nr', '--new_row', default=True, type=boolparse, help='Whether to use the active row or create a new one.')
    @argument('-nc', '--new_col', default=True, type=boolparse, help='Whether to use the active col or create a new one.')
    @argument('-s', '--size', default=None, type=int, help='The size of the column in the row.')
    @argument('-l', '--latex', default=False, type=boolparse, help='Whether to evaluate LaTeX expresions. Only valid if cell output is a string.')
    @argument('-h', '--html', default=False, type=boolparse, help='Whether to  evaluate input as raw HTML rather than markdown. Only valid if cell output is a string.')
    @argument('-cap', '--caption', default=None, type=strparse, help='Caption for a DataFrame or Figure.')
    @argument('-o', '--overwrite', default=False, type=boolparse, help='Whether to overwrite the given column. Only valid if col is not None.')
    @argument('-cp', '--copy', default=False, type=boolparse, help='Whether to copy the input object before inserting to the report.')
    @line_cell_magic
    def bake(self, line, cell=None, local_ns=None):
        """
        IPython Magic that serves as a direct interface for adding elements to a BakePy Report.
        """
        if cell is None:
            print("Called as line magic")
        else:
            print("Called as cell magic")
        args = parse_argstring(self.bake, line)

        print(args)
        if args.report is not None:
            local_ns[args.report] = "REPORT"
        print("My results are:")
        print(markdown.markdown(eval(cell, None, local_ns)))
    
    #Set cls/sty and other things like active reports, etc...
    @needs_local_scope
    @magic_arguments()
    @argument('-R', '--report', default=None, type=idparse, help='The name of the report to use. If it does not exist, it is created. If None, uses the current active report. Must be a valid Python identifier name.')
    @argument('-C', '--container', default=None, type=strparse, help='The name of the container to use. If it does not exist, it is created.')
    @argument('-r', '--row', default=None, type=int, help='The row position to use. If none provided, uses the current row.')
    @argument('-c', '--col', default=None, type=int, help='The position to take in the row. If none provided, inserts at the end of the current row.')
    @line_cell_magic
    def bake_set(self, line, cell=None, local_ns=None):
        """
        IPython Magic that serves as a direct interface for setting operations in a BakePy Report.
        """
        if cell is None:
            print("Called as line magic")
        else:
            print("Called as cell magic")
        args = parse_argstring(self.bake, line)

        print(args)
        if args.report is not None:
            local_ns[args.report] = "REPORT"
        print("My results are:")
        print(markdown.markdown(eval(cell, None, local_ns)))
    
    #Remove reports, containers, rows, and columns
    @needs_local_scope
    @magic_arguments()
    @argument('-R', '--report', default=None, type=idparse, help='The name of the report to use. If it does not exist, it is created. If None, uses the current active report. Must be a valid Python identifier name.')
    @argument('-C', '--container', default=None, type=strparse, help='The name of the container to use. If it does not exist, it is created.')
    @argument('-r', '--row', default=None, type=int, help='The row position to use. If none provided, uses the current row.')
    @argument('-c', '--col', default=None, type=int, help='The position to take in the row. If none provided, inserts at the end of the current row.')
    @line_cell_magic
    def bake_rem(self, line, cell=None, local_ns=None):
        """
        IPython Magic that serves as a direct interface for remove operations in a BakePy Report.
        """
        if cell is None:
            print("Called as line magic")
        else:
            print("Called as cell magic")
        args = parse_argstring(self.bake, line)

        print(args)
        if args.report is not None:
            local_ns[args.report] = "REPORT"
        print("My results are:")
        print(markdown.markdown(eval(cell, None, local_ns)))

    #Save the report
    @needs_local_scope
    @magic_arguments()
    @argument('-R', '--report', default=None, type=idparse, help='The name of the report to use. If it does not exist, it is created. If None, uses the current active report. Must be a valid Python identifier name.')
    @argument('-f', '--filetype', default=None, type=strparse, help='The name of the container to use. If it does not exist, it is created.')
    @argument('-p', '--path', default=None, type=strparse, help='The row position to use. If none provided, uses the current row.')
    @argument('-e', '--embed', default=None, type=boolparse, help='The position to take in the row. If none provided, inserts at the end of the current row.')
    @line_cell_magic
    def bake_save(self, line, cell=None, local_ns=None):
        """
        IPython Magic that serves as a direct interface for saving operations in a BakePy Report.
        """
        if cell is None:
            print("Called as line magic")
        else:
            print("Called as cell magic")
        args = parse_argstring(self.bake, line)

        print(args)
        if args.report is not None:
            local_ns[args.report] = "REPORT"
        print("My results are:")
        print(markdown.markdown(eval(cell, None, local_ns)))