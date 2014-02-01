import sublime, sublime_plugin
import uuid
from sublime import Region

def genUUID(version = 4):
  result = None
  if version is 1:
    result = uuid.uuid1()
  elif version is 3:
    result = uuid.uuid3()
  elif version is 4:
    result = uuid.uuid4()
  # elif version is 5:
  #   result = uuid.uuid5(...)
  else:
    raise ValueError("Invalid or unsupported UUID version")
  return result

class InsertUuidCommand(sublime_plugin.TextCommand):
  def run(self, edit, version = 4):
    view = self.view
    view_sels = view.sel()
    sels = []
    for region in reversed(view_sels):
      delta = 0
      point = region.begin()
      if not region.empty():
        view.erase(edit, region)
        delta -= region.size()

      inserted = view.insert(edit, point, str(genUUID(version)))
      delta += inserted
      new_region = Region(point, point + inserted)

      for sel in sels:
        sel.a += delta
        sel.b += delta

      sels.append(new_region)

    view_sels.clear()
    view_sels.add_all(sels)
