try:
    import colorama
except ImportError:
    colorama = None

import io


class ColorText(object):
    """Render colored text output.

    Only works if you have
    `colorama <https://pypi.python.org/pypi/colorama>`_ installed, otherwise,
    the text will be printed without color.  This way, you can use this library
    and not have to worry about whether or not they have colorama installed.
    If they do, the text will be in color, if they don't, it won't.

    Example:

    >>> from frf.utils.cli.colors import ColorText
    >>> col = ColorText()
    >>> print(col.green('hello ').red('world!').value())
    'hello world!'
    >>>
    """
    def __init__(self):
        self.io = io.StringIO()

    def append_text(self, text, color=None):
        if color is None and colorama:
            color = 'RESET'

        if colorama:
            color = getattr(colorama.Fore, color)

        if colorama:
            self.io.write(color + text + colorama.Fore.RESET)
        else:
            self.io.write(text)

        return self

    def lightmagenta(self, text):
        return self.append_text(text, color='LIGHTMAGENTA_EX')

    def green(self, text):
        return self.append_text(text, color='GREEN')

    def red(self, text):
        return self.append_text(text, color='RED')

    def blue(self, text):
        return self.append_text(text, color='BLUE')

    def lightblue(self, text):
        return self.append_text(text, color='LIGHTBLUE_EX')

    def yellow(self, text):
        return self.append_text(text, color='YELLOW')

    def reset(self, text):
        return self.append_text(text)

    def lightgreen(self, text):
        return self.append_text(text, color='LIGHTGREEN')

    def value(self, close=True):
        val = self.io.getvalue()
        self.io.close()
        self.io = io.StringIO()
        return val
