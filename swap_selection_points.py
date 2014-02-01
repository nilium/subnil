import sublime, sublime_plugin

def region_start(region, mode = None):
  if mode:
    if mode == 'max': return region.begin()
    elif mode == 'min': return region.end()
    elif mode == 'swap': return region.b

  return region.a

def region_end(region, mode = None):
  if mode:
    if mode == 'max': return region.end()
    elif mode == 'min': return region.begin()
    elif mode == 'swap': return region.a

  return region.b

def adjusted_region(region, mode = None, nth = None):
  if type(nth) is list:
    nth[0] += 1
    nth = nth[0]

  if mode and nth:
    if mode == 'even' or mode == 'odd':
      if mode == 'odd': nth += 1
      mode = 'min' if nth % 2 == 0 else 'max'

  return sublime.Region(region_start(region, mode), region_end(region, mode))

class SwapSelectionPointsCommand(sublime_plugin.TextCommand):
  def run(self, edit, mode = None):
    """
    Swaps the caret position for given regions, which is actually just swapping
    the points of the selection. `mode` may be any of the following, or None to
    use the default value.

      mode = swap (default) | min | max | odd | even
      - swap swaps the position of all carets. (default)
      - min puts the caret of all selections at their minimum point/start.
      - max puts the caret of all selections at their maximum point/end.
      - odd puts all odd carets at the min and even at the max.
      - even does the opposite of odd.
    """

    if not mode: mode = 'swap'

    sel = self.view.sel()
    regions = list(sel)
    sel.clear()
    nth = [0]
    sel.add_all(adjusted_region(r, mode, nth) for r in regions)
