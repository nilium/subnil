import sublime, sublime_plugin
from sublime import RegionSet

class StoreSelectionCommand(sublime_plugin.TextCommand):
  def __init__(self, p):
    super(StoreSelectionCommand, self).__init__(p)
    self._selections = None

  def run(self, edit, restore = False):
    view = self.view
    view_sel = view.sel()
    if restore and self._selections:
      view_sel.clear()
      for region in self._selections:
        view_sel.add(region)
    else:
      self._selections = [region for region in view.sel()]
