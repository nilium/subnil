Notes
==========================

Commands
--------------------------

### `swap_theme`

**Under the quick panel as "Set Dark Theme" and "Set Light Theme"**

Swaps your current theme for given dark or light theme settings.  Relevant
settings for that:

* `light_color_scheme` and `dark_color_scheme` specify your light & dark color
  schemes respectively.  Defaults to Dawn and Monokai respectively.

* `light_theme` and `dark_theme` specify the light & dark UI themes
  respectively.  Defaults to the default theme.

### `insert_license`

**Under the quick panel as "License: Insert License"**

Inserts one of the specified licenses at the insertion point (or replaces
whatever you have selected).  Fairly simply.

Settings for `insert_license`:

* `wrap_width`: If greater than 1, the license text will be wrapped to that
    width.

* `full_name`: Your name.  Defaults to "A Nameless Jerk" just to encourage you
    to change it.

* `project_name`: Your project's name.  Should be in project settings.
    Defaults to "this program" -- only used for GPL licenses.  No need to set
    it otherwise.

* `license_wrap`: The column width the license is wrapped to.  Maybe you
    dislike enabling word-wrap and it only applies to your license header. What
    the hell do I know?  Defaults to 80 because I'm going to make you wrap your
    damned license.


### `include_once`

**Under the quick panel as "C: Include Once"**

Generates include guards for the file this is run in.  If you've got text
selected already, it'll wrap it in the include guards.

