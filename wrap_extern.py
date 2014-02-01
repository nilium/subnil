import sublime, sublime_plugin
import re

class WrapExternCommand(sublime_plugin.TextCommand):
	ONCE_SNIPPET = '''#ifdef __cplusplus
extern "C" {{
#endif /* __cplusplus */

$0{inner}

#ifdef __cplusplus
}}
#endif /* __cplusplus */
'''

	def run(self, edit):
		selection = self.view.sel()
		inner_text = ''
		
		for region in selection:
			inner_text = self.view.substr(self.view.line(region))
			break
		
		guard = WrapExternCommand.ONCE_SNIPPET.format(inner = inner_text)
		self.view.run_command('insert_snippet', {'contents':guard})
