import sublime, sublime_plugin

class SwapThemeCommand(sublime_plugin.ApplicationCommand):
  defaults = {
    "light": ("Packages/Color Scheme - Default/Cobalt.tmTheme", "Default.sublime-theme"),
    "dark": ("Packages/Color Scheme - Default/Monokai.tmTheme", "Default.sublime-theme")
  }

  def run(self, scheme):
    if not (scheme == "light" or scheme == "dark"):
      return

    colors = SwapThemeCommand.defaults[scheme][0]
    theme = SwapThemeCommand.defaults[scheme][1]

    settings = sublime.load_settings("Preferences.sublime-settings")

    colors = settings.get(scheme+"_color_scheme", colors)
    theme = settings.get(scheme+"_theme", theme)

    settings.set("color_scheme", colors)
    settings.set("theme", theme)

    sublime.save_settings("Preferences.sublime-settings")

    self.set_theme(colors, theme)

  def set_theme(self, colors, theme):
    print "foobar!"
    for window in sublime.windows():
      for view in window.views():
        settings = view.settings()
        settings.set("theme", theme)
        settings.set("color_scheme", colors)
