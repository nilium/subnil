import sublime, sublime_plugin
import textwrap
import string
from datetime import date

# Relevant settings:
# wrap_width -> If greater than 1, the license text will be wrapped to that width.
# full_name -> Your name.  Defaults to "A Nameless Jerk" just to encourage you to change it.
# project_name -> Your project's name.  Should be in project settings.  Defaults to "this program" -- only used for GPL licenses.  No need to set it otherwise.
# license_wrap -> The column width the license is wrapped to.  Maybe you dislike enabling word-wrap and it only applies to your license header.  What the hell do I know?  Defaults to 80 because I'm going to make you wrap your damned license.

class InsertLicenseCommand(sublime_plugin.TextCommand):
	licenses = {
		'MIT License':'''Copyright (c) %(year)s %(name)s

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.''',

		'BSD License':'''Copyright (c) %(year)s, %(name)s
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.''',

		'zlib/libpng License':'''Copyright (c) %(year)s %(name)s

This software is provided 'as-is', without any express or implied warranty. In no event will the authors be held liable for any damages arising from the use of this software.

Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter it and redistribute it freely, subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If you use this software in a product, an acknowledgment in the product documentation would be appreciated but is not required.

2. Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.

3. This notice may not be removed or altered from any source distribution.''',

	'GPLv2 License': '''Copyright (C) %(year)s %(name)s

%(cap_project)s is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

%(project)s is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with %(project)s; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.''',

	'GPLv3 License': '''Copyright (C) %(year)s %(name)s

%(cap_project)s is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

%(cap_project)s is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with %(project)s.  If not, see <http://www.gnu.org/licenses/>.''',

    'LGPLv2 License': '''Copyright (C) %(year)s %(name)s

This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation; either version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA''',

	'Do What The Fuck You Want To License (WTFPL)': '''Copyright (C) %(year)s %(name)s

Everyone is permitted to copy and distribute verbatim or modified copies of this license document, and changing it is allowed as long as the name is changed.

DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

0. You just DO WHAT THE FUCK YOU WANT TO.'''
	}

	def run(self, edit):
		self.keys = InsertLicenseCommand.licenses.keys()
		self.keys.sort()
		self.edit = edit
		wnd = self.view.window()
		wnd.show_quick_panel(self.keys, self.license_picked)

	def license_picked(self, index):
		if index is -1:
			return

		settings = self.view.settings()

		edit = self.edit
		key = self.keys[index]

		license = InsertLicenseCommand.licenses[key]
		# Project name (used only by gpl licenses)
		project_name = settings.get('project_name', 'This program')

		format_opts = {
			'project': project_name,
			# capitalized project name (mainly just for GPL licenses)
			'cap_project': string.capitalize(project_name),
			# user's name, including a tasteless default
			'name': settings.get('full_name', 'A Nameless Jerk'),
			# the current year for the copyright
			'year': date.today().year
		}

		# format license
		text = license % format_opts

		# wrap text to wrap_width if specified
		wrap_width = int(settings.get('wrap_width', 80)) 
		if wrap_width is 0:
			wrap_width = int(settings.get('license_wrap', 80))

		if wrap_width > 0:
			wrap_width -= 1
			wraps = [textwrap.fill(line, wrap_width) for line in text.splitlines(True)]
			text = string.join(wraps, "\n")

		# insert/replace text as needed
		for region in self.view.sel():
			if region.empty():
				self.view.insert(edit, region.begin(), text)
			else:
				self.view.replace(edit, region, text)

