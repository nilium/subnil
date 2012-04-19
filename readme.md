Notes
==========================

The Theme
--------------------------

_Tubnil_: This is a modified version of the Tubster theme for TextMate.  Kind of hard to describe, so here's a picture:

![Tubnil Screenshot](http://www.spifftastic.net/skitch/tubnil-20120419-033143.png)


Commands
--------------------------

### `insert_license`

Inserts one of the specified licenses at the insertion point (or replaces whatever you have selected).  Fairly simply.

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

Generates include guards for the file this is run in.  If you've got text selected already, it'll wrap it in the include guards.
