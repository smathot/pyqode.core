# -*- coding: utf-8 -*-
"""
This module contains the breakpoints checker mode
"""
from qtpy import QtCore, QtGui
from pyqode.core.modes import CheckerMode, CheckerMessage, CheckerMessages


class BreakpointMode(CheckerMode):
    """This checker mode shows all the breakpoints defined for this document.
    Unlike the other checker modes, this does not use a separate worker process
    because there is very little work to do. Instead, the CheckerMode class is
    used as a convenient way to annotate the margins.
    """
    
    breakpoint_toggled = QtCore.Signal(str, int)
    BREAKPOINT_MESSAGE = '[BREAKPOINT]'
    
    def __init__(self, breakpoints={}, keyboard_shortcut=QtCore.Qt.Key_F12):
        
        CheckerMode.__init__(self, None)
        self._breakpoints = breakpoints
        self._keyboard_shortcut = (
            QtGui.QKeySequence(keyboard_shortcut)
            if isinstance(keyboard_shortcut, str)
            else keyboard_shortcut
        )

    def on_state_changed(self, state):
        
        if state:
            self.editor.key_pressed.connect(self._on_key_pressed)
            self.editor.textChanged.connect(self.request_analysis)
            self.editor.new_text_set.connect(self.clear_messages)
            self.request_analysis()
        else:
            self.editor.key_pressed.disconnect(self._on_key_pressed)
            self.editor.textChanged.disconnect(self.request_analysis)
            self.editor.new_text_set.disconnect(self.clear_messages)
            self.clear_messages()

    def _request(self):

        self._finished = True
        path = self.editor.file.path
        if path not in self._breakpoints:
            return []
        messages = []
        block_count = self.editor.blockCount()
        document = self.editor.document()
        for line in self._breakpoints[path]:
            if line >= block_count:
                oslogger.debug(
                    'breakpoint out of document: {}:{}'.format(path, line)
                )
                continue
            msg = CheckerMessage(
                description=self.BREAKPOINT_MESSAGE,
                status=CheckerMessages.INFO,
                line=line,
                block=document.findBlockByNumber(line),
                underline=False
            )
            messages.append(msg)
        self.add_messages(messages)

    def _on_key_pressed(self, event):

        if (
            self._keyboard_shortcut.matches(event.key()) !=
            self._keyboard_shortcut.ExactMatch
        ):
            return
        line = self.editor.textCursor().blockNumber()
        path = self.editor.file.path
        if path not in self._breakpoints:
            self._breakpoints[path] = []
        if line in self._breakpoints[path]:
            self._breakpoints[path].remove(line)
        else:
            self._breakpoints[path].append(line)
        self.request_analysis()
        self.breakpoint_toggled.emit(path, line)
