import sublime, sublime_plugin
from math import ceil

def banner_comment_width(max_content_length, min_width, padding, wall_padding, comment):
  width = (
    max_content_length
    + (padding * 2)
    + (wall_padding * 2)
    + len(comment[0]) + len(comment[1])
    )

  if min_width and min_width > width:
    width = min_width

  return width

def pad_string(string, min_padding, width):
  ws_desired = width - len(string)
  ws_length = max(min_padding, ws_desired)
  return string + (' ' * ws_length)

def banner_comment(contents, wall_padding = None, padding = None, comment = None, width = None):
  # This code is terrible.
  if comment is None: comment = adjust_comment(('#', None, None, None))
  if padding is None: padding = 1
  if wall_padding is None: wall_padding = 1

  is_block = comment_is_block(comment)

  start = comment[0]
  finish = comment[1]
  wall_text = comment[2]
  outer_text = comment[3]
  prefix = comment_prefix(comment, wall_padding > 0)
  mid_prefix = comment_prefix(comment, wall_padding > 0, True)
  prefix_len = max(len(prefix), len(mid_prefix))
  prefix = repeat_to_length(prefix, prefix_len)
  mid_prefix = repeat_to_length(mid_prefix, prefix_len)

  wall_pad_repeats = ceil(wall_padding / len(wall_text))
  max_content_len = max(len(content) for content in contents)

  pad_str = ' ' * padding
  outer_pad_str = (wall_text * wall_pad_repeats)[:wall_padding]

  banner_width_hint = banner_comment_width(max_content_len, width, padding, wall_padding, comment)
  banner_width_hint -= len(prefix)

  lpad_str = outer_pad_str + pad_str
  middles = [(mid_prefix + lpad_str + content).strip() for content in contents]

  if wall_padding > 0 and len(wall_text) > 0:
    padded_width = banner_width_hint - len(outer_pad_str)
    middles = [(pad_string(middle, padding, padded_width) + outer_pad_str).strip() for middle in middles]

  mid_len = max(len(middles[0]), banner_width_hint)

  start_str = start + repeat_to_length(outer_text, mid_len - len(start))
  end_str = prefix + repeat_to_length(outer_text, mid_len - len(finish) - len(prefix)) + finish

  return [start_str] + middles + [end_str]

def repeat_to_length(repeated, to_length):
  if not repeated or len(repeated) == 0:
    return ''

  if len(repeated) == to_length:
    return repeated

  return (repeated * ceil(to_length / len(repeated)))[:to_length]

def env_vars(view, at_point):
  evars = view.meta_info("shellVariables", at_point)
  r = {}
  for v in evars:
    r[v['name']] = v['value']
  return r

def env_comment_segments(view, at_point = 0):
  # based off the comment-info-fetching code in the default comment.py plugin
  env = env_vars(view, at_point)

  # default and then alternatives -- looking for block syntax, preferably
  indices = [''] + ['_' + str(index) for index in range(10)]
  best = (None, None, None, None)
  for index in indices:
    key_start = 'TM_COMMENT_START' + index
    key_end = 'TM_COMMENT_END' + index
    start = str(env[key_start]) if key_start in env else None
    finish = str(env[key_end]) if key_end in env else None

    if best[0] is None or (best[1] is None and finish is not None):
      best = (start, finish, None, None)

    if start and finish:
      return best

  return best

def line_for(view, region, indent = None):
  linestr = view.substr(region)
  linelen = len(linestr)

  if region.empty():
    return region

  if indent is None:
    indent = 0
    while indent < linelen and (linestr[indent] == ' ' or linestr[indent] == '\t'):
      indent = indent + 1

  if region.a == region.begin():
    region.a += indent
  else:
    region.b += indent

  return region

def filter_empty(regions):
  return [r for r in regions if not r.empty()]

def line_strings(view, region, indent):
  return [view.substr(line_for(view, view.line(r), indent = indent)) for r in view.split_by_newlines(region)]

def min_column_in_region(view, region):
  lines = filter_empty(view.line(r) for r in view.split_by_newlines(region))
  if len(lines) > 0:
    return min(view.rowcol(line_for(view, r).begin())[1] for r in lines)
  else:
    return 0

def comment_prefix(cdata, walled = False, in_wall = False):
  prefix = ''
  if not comment_is_block(cdata):
    prefix = cdata[0]

    if walled and prefix == (cdata[2] if in_wall else cdata[3]):
      prefix = ''

  return prefix

def adjusted_strip(string, strip):
  if strip:
    if strip == 'both':
      return string.strip()
    elif strip == 'left':
      return string.lstrip()
    elif strip == 'right':
      return string.rstrip()
  return string

def adjust_comment(cdata, strips = None):
  is_block = comment_is_block(cdata)
  if type(strips) is tuple:
    if strips and len(strips) < 1:
      strips = (None, None)
    elif strips and len(strips) < 2:
      strips = (strips[0], None)
  elif strips:
    strips = (strips, strips)
  else:
    strips = ('both', 'both')

  start = adjusted_strip(cdata[0], strips[0])
  finish = adjusted_strip(cdata[1], strips[1]) if is_block else ''

  # use these for checking matching prefix/suffix
  stripped_start = start.strip()
  stripped_finish = finish.strip()

  wall_text = cdata[2] if len(cdata) >= 3 else None
  if wall_text is None:
    if is_block and stripped_start[-1] == stripped_finish[0]:
      wall_text = stripped_start[-1]
    else:
      wall_text = stripped_start[0]

  outer_text = wall_text if len(cdata) < 4 or not cdata[3] else cdata[3]

  return (start, finish, wall_text, outer_text)

def comment_is_block(cdata):
  return len(cdata) >= 2 and cdata[0] and cdata[1] and len(cdata[1]) > 0

def indent_text(view, width, use_spaces = None):
  if use_spaces is None:
    use_spaces = view.settings().get("translate_tabs_to_spaces", True)

  if use_spaces:
    return ' ' * width
  else:
    return '\t' * width

class WrapInBannerCommentCommand(sublime_plugin.TextCommand):
  #############################################################################
  #  Valid Options:
  #  - `banner_comment_style`
  #      A one to four element array. The first element must be a string
  #      marking the beginning of a comment. If the second element is null,
  #      comments are inserted as line comments, otherwise the first element
  #      must begin a block comment and the second element must end the block
  #      comment. The third element is the repeating character, which overrides
  #      both banner_comment_wall_padding_text and the default. If null,
  #      either banner_comment_wall_padding_text is used if set, otherwise
  #      the first character of the line comment is used unless the last
  #      block comment ends with the same character as the last character of
  #      the block comment decl. In other words, for example, it'll use
  #      * for /*...*/ in C, but it'll use - for --[[...]] in Lua.
  #
  #      The fourth element is outer text, which is only used for the top and
  #      bottom edges of the banner. If none is specified, it uses the wall
  #      text (third element, used for the left/right sides).
  #
  #  - `banner_comment_stripped`
  #     Either a string or an array. If null or unset, defaults to
  #     ['both', 'both']. This determines which sides of the syntax's defined
  #     comment style is stripped of whitespace. So, for example, with XML,
  #     you'd want to set this to ['none', 'none'] to keep whitespace after
  #     and before the start and finish of the comment block, respectively,
  #     since <!---- ----> is invalid. Valid strip options are 'left', 'right',
  #     and 'both' and each element of the stripped array applies to the start
  #     and end blocks of a block comment (or the start of a line comment).
  #     Invalid values in the array are treated as though you do not want
  #     whitespace stripped.
  #
  #  - `banner_comment_padding`
  #      The amount of whitespace, minimum, between the walls of the banner
  #      and its lines. Comment banners have at least this many spaces on
  #      their right sides to keep the walls aligned.
  #
  #  - `banner_comment_wall_padding`
  #      The width of the padding text used around comment banners' contents.
  #
  #  - `banner_comment_wall_text`, `banner_comment_outer_text`
  #      The text to wrap comment banners in. This is repeated on the sides,
  #      above, and below comment banners. May be any length. This overrides
  #      default text extracted from comment syntax. See banner_comment_style
  #      above for a crude explanation of how this works. Remember: outer is
  #      the top/bottom and defaults to the wall text. Wall text is left/right,
  #      and defaults to something that matches in the extracted comment style.
  #
  #  - `banner_comment_width`
  #      The width of comment banners. If not set, defaults to the wrap_width
  #      or nothing, if neither are set. When neither are set, the banner
  #      simply wraps encompasses all lines in the banner and does not
  #      attempt to fill out space for short banners.
  #
  #  - `banner_comment_skip_indent`
  #      If true, banner comments always begin at column zero, otherwise they
  #      start at minimum column of the text being turned into a banner
  #      comment. Defaults to false.
  #############################################################################

  def insert_banner(self, edit, region, banner):
    view = self.view
    view.erase(edit, region)

    insert_point = region.begin()
    sel_start = insert_point

    for line in banner:
      insert_point += view.insert(edit, insert_point, line + '\n')

    sel_end = insert_point - 1

    return sublime.Region(sel_start, sel_end)

  def run(self, edit, comment = None, padding = None, width = None, wall_padding = None, skip_indent = None, stripped = None):
    view = self.view
    sels = [] # new selections after banner-izing things

    settings = view.settings()
    use_spaces = settings.get("translate_tabs_to_spaces", True)
    tab_size = settings.get("tab_size", 4)

    # Get setting defaults
    outer_text = settings.get('banner_comment_outer_text', None)
    wall_text = settings.get('banner_comment_wall_text', None)

    if padding is None:
      padding = settings.get('banner_comment_padding', tab_size)

    if wall_padding is None:
      wall_padding = settings.get('banner_comment_wall_padding', 1)

    if skip_indent is None:
      skip_indent = settings.get('banner_comment_skip_indent', False)

    if width is None:
      width = settings.get('banner_comment_width', settings.get('wrap_width', None))
      # If it's set to 0 or less, use 78. If it's actually nothing, use 0.
      if width and width <= 0:
        width = 78
      elif not width:
        width = 0

    if stripped is None:
      stripped = settings.get('banner_comment_stripped')

    if comment is None:
      comment = settings.get('banner_comment_style')
      if comment:
        comment = adjust_comment(comment, stripped)

    # Process selections in reverse so it's easier to update selections as the
    # plugin replaces them with banner comments.
    for region in reversed(view.sel()):
      indent_text_len = min_column_in_region(view, region)
      indent_str = ''
      if not skip_indent:
        indent_str = indent_text(view, indent_text_len, use_spaces = use_spaces)

      indent_column = indent_text_len
      if not use_spaces:
        indent_column = indent_text_len * tab_size

      indented_width = width
      if not skip_indent and width is not None:
        indented_width = width - indent_column

      local_comment = comment
      if not local_comment:
        local_comment = env_comment_segments(view, region.begin())

      # Skip selections where the comment is undefined
      if local_comment is None or local_comment[0] is None:
        sels.append(region)
        continue

      # Swap in outer_text iff the comment style doesn't already define one.
      if len(local_comment) < 3 or local_comment[2] is None:
        if len(local_comment) < 4:
          local_comment = (local_comment[0], local_comment[1], wall_text, outer_text)
        else:
          local_comment = (local_comment[0], local_comment[1], wall_text, local_comment[3])

      if outer_text:
        print("setting outer text")
        local_comment = (local_comment[0], local_comment[1], local_comment[2], outer_text)

      if local_comment:
        local_comment = adjust_comment(local_comment, stripped)

      # Create a list of banner lines.
      banner_lines = banner_comment(
        line_strings(view, region, indent = indent_text_len),
        width = indented_width,
        comment = local_comment,
        wall_padding = wall_padding,
        padding = padding
        )

      # Indent banner lines
      if indent_text_len > 0:
        banner_lines = [indent_str + line for line in banner_lines]

      region = view.full_line(region)
      old_size = region.size()
      banner_region = self.insert_banner(edit, region, banner_lines)

      # Since banners are inserted in reverse, it's easy enough to update the
      # new selection regions with deltas from this insertion.
      # The + 1 is to account for newlines at the end of the banners.
      delta = (banner_region.size() + 1) - old_size
      for new_sel in sels:
        new_sel.a += delta
        new_sel.b += delta

      banner_region.a += len(indent_str)
      sels.append(banner_region)

    sel = view.sel()
    sel.clear()
    sel.add_all(sels)
