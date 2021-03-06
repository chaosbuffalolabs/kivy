# -*- coding: utf-8 -*-
'''
Code Input
==========

.. versionadded:: 1.5.0

.. image:: images/codeinput.jpg


The :class:`CodeInput` provides a box of editable highlited text, like the ones
shown in the image.

It supports all the features supported by the :class:`~kivy.uix.textinput` and
Code highliting for `languages supported by pygments
<http://pygments.org/docs/lexers/>`_ along with `KivyLexer` for `KV Language`
highliting.

Usage example
-------------

To create a CodeInput with highliting for `KV language`::

    from kivy.uix.codeinput import CodeInput
    from kivy.extras.highlight import KivyLexer
    codeinput = CodeInput(lexer=KivyLexer())

To create a CodeInput with highliting for `Cython`::

    from kivy.uix.codeinput import CodeInput
    from pygments.lexers import CythonLexer
    codeinput = CodeInput(lexer=CythonLexer())

'''

__all__ = ('CodeInput', )

from pygments import highlight
from pygments import lexers
from pygments.formatters import BBCodeFormatter

from kivy.uix.textinput import TextInput
from kivy.core.text.markup import MarkupLabel as Label
from kivy.cache import Cache
from kivy.properties import ObjectProperty

Cache_get = Cache.get
Cache_append = Cache.append

# TODO: fix empty line rendering
# TODO: color chooser for keywords/strings/...


class CodeInput(TextInput):
    '''CodeInput class, used for displaying highlited code.
    '''

    lexer = ObjectProperty(None)
    '''This holds the selected Lexer used by pygments to highlite the code


    :data:`lexer` is a :class:`~kivy.properties.ObjectProperty` defaults to
    `PythonLexer`
    '''

    def __init__(self, **kwargs):
        self.formatter = BBCodeFormatter()
        self.lexer = lexers.PythonLexer()
        self.text_color = '#000000'
        self._label_cached = Label()
        self.use_text_color = True
        super(CodeInput, self).__init__(**kwargs)
        self._line_options = kw = self._get_line_options()
        self._label_cached = Label(**kw)
        # use text_color as foreground color
        text_color = kwargs.get('foreground_color')
        if text_color:
            get_hex_clr = self.get_hex_clr
            self.text_color = ''.join(('#',
                get_hex_clr(text_color[0]),
                get_hex_clr(text_color[1]),
                get_hex_clr(text_color[2]),
                get_hex_clr(text_color[3])))
        # set foreground to white to allow text colors to show
        # use text_color as the default color in bbcodes
        self.use_text_color = False
        self.foreground_color = [1, 1, 1, .999]
        if not kwargs.get('background_color'):
            self.background_color = [.9, .92, .92, 1]

    def get_hex_clr(self, color):
        clr = hex(int(color * 255))[2:]
        if len(str(clr)) < 2:
            clr = ''.join(('0', str(clr)))
        return clr

    def _create_line_label(self, text):
        # Create a label from a text, using line options
        ntext = text.replace('\n', '').replace('\t', ' ' * self.tab_width)
        if self.password:
            ntext = '*' * len(ntext)
        ntext = self._get_bbcode(ntext)
        kw = self._get_line_options()
        cid = '%s\0%s' % (ntext, str(kw))
        texture = Cache_get('textinput.label', cid)

        if not texture:
            # FIXME right now, we can't render very long line...
            # if we move on "VBO" version as fallback, we won't need to do this.
            # try to found the maximum text we can handle
            label = Label(text=ntext, **kw)
            if text.find('\n') > 0:
                label.text = ''
            else:
                label.text = ntext
            try:
                label.refresh()
            except ValueError:
                return

            # ok, we found it.
            texture = label.texture
            Cache_append('textinput.label', cid, texture)
            label.text = ''
        return texture

    def _get_line_options(self):
        kw = super(CodeInput, self)._get_line_options()
        kw['markup'] = True
        kw['valign'] = 'top'
        kw['codeinput'] = True
        return kw

    def _get_bbcode(self, ntext):
        # get bbcoded text for python
        try:
            ntext[0]
            # replace brackets with special chars that aren't highlighted
            # by pygment. can't use &bl; ... cause & is highlighted
            # if at some time support for braille is added then replace these
            # characters with something else
            ntext = ntext.replace('[', u'⣿;').replace(']', u'⣾;')
            ntext = highlight(ntext, self.lexer, self.formatter)
            ntext = ntext.replace(u'⣿;', '&bl;').replace(u'⣾;', '&br;')
            # replace special chars with &bl; and &br;
            ntext = ''.join(('[color=', str(self.text_color), ']',
                             ntext, '[/color]'))
            ntext = ntext.replace('\n', '')
            return ntext
        except IndexError:
            return ''

    # overriden to prevent cursor position off screen
    def _cursor_offset(self):
        '''Get the cursor x offset on the current line
        '''
        offset = 0
        try:
            if self.cursor_col:
                offset = self._get_text_width(
                    self._lines[self.cursor_row][:self.cursor_col])
        except:
            pass
        finally:
            return offset

    def on_lexer(self, instance, value):
        self._trigger_refresh_text()

    def on_foreground_color(self, instance, text_color):
        if not self.use_text_color:
            self.use_text_color = True
            return
        get_hex_clr = self.get_hex_clr
        self.text_color = ''.join((
                get_hex_clr(text_color[0]),
                get_hex_clr(text_color[1]),
                get_hex_clr(text_color[2]),
                get_hex_clr(text_color[3])))
        self.use_text_color = False
        self.foreground_color = (1, 1, 1, .999)
        self._trigger_refresh_text()


if __name__ == '__main__':
    from kivy.extras.highlight import KivyLexer
    from kivy.app import App

    class CodeInputTest(App):
        def build(self):
            return CodeInput(lexer=KivyLexer(),
                font_name='data/fonts/DroidSansMono.ttf', font_size=12,
                text='''
#:kivy 1.0

<YourWidget>:
    canvas:
        Color:
            rgb: .5, .5, .5
        Rectangle:
            pos: self.pos
            size: self.size''')

    CodeInputTest().run()
