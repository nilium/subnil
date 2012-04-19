import sublime, sublime_plugin
import re
import os

class IncludeOnceCommand(sublime_plugin.TextCommand):
	ONCE_SNIPPET = '''#ifndef ${{1:__{guard_name}__}}
#define $1

$0{inner}

#endif /* end $1 include guard */
'''

	def run(self, edit):
		name = self.view.file_name()
		
		if name is None:
			name = 'UNTITLED'
		else:
			name = os.path.basename(name.upper())

		name = re.sub('[^\w]+', '_', name)

		selection = self.view.sel()
		inner_text = ''
		
		for region in selection:
			inner_text = self.view.substr(self.view.line(region))
			break
		
		guard = IncludeOnceCommand.ONCE_SNIPPET.format(guard_name = name, inner = inner_text)
		self.view.run_command('insert_snippet', {'contents':guard})
