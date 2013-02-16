# bounded_grab_next.py
import sublime, sublime_plugin, re

class BoundedGrabNextCommand(sublime_plugin.TextCommand):
  def __init__(self, p):
    super(BoundedGrabNextCommand, self).__init__(p)
    self._last_word = None
    self._last_regex = None
  #/__init__

  def run(self, edit, skip_last = False):
    last_selection = None
    view = self.view

    selections = view.sel()
    last_selection = selections[-1]

    # If the last selection is empty, expand to the current word. In other
    # words, just do the usual Cmd+D operation.
    if last_selection.a == last_selection.b:
      view.window().run_command('find_under_expand')
      return
    #/if

    regex = None
    word = view.substr(last_selection)
    if self._last_word == word:
      regex = self._last_regex
    else:
      regex = "\\b{0}\\b".format(re.escape(word))
    #/if

    if skip_last:
      selections.subtract(last_selection)
    #/if

    last_point = max(last_selection.a, last_selection.b)
    next_find = view.find(regex, last_point)
    if next_find is None:
      next_find = view.find(regex, 0)

      while next_find and selections.contains(next_find):
        next_find = view.find(regex, next_find.b)
      #/while
    #/if

    if next_find:
      selections.add(next_find)
      view.show(next_find)
    #/if

    self._last_word = word
    self._last_regex = regex
  #/run
#/BoundedGrabNextCommand
