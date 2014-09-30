import sublime, sublime_plugin, re

def getViewRegion(view): return sublime.Region(0, view.size())
def getViewContent(view): return view.substr(getViewRegion(view))

# Enters block mode by appending whitespace to every line
class ToggleBlockMode(sublime_plugin.TextCommand):
   currentModeKey = "current_block_mode"
   def run(self,edit):
      settings = self.view.settings();
      if settings.has(self.currentModeKey):
         settings.set(self.currentModeKey, not settings.get(self.currentModeKey))
      else:
         settings.set(self.currentModeKey,True)
      if(settings.get(self.currentModeKey)):
         self.view.run_command('enter_block_mode')
      else:
         self.view.run_command('exit_block_mode')

# Enters block mode by appending whitespace to every line
class EnterBlockMode(sublime_plugin.TextCommand):
   def run(self,edit):
      content = getViewContent(self.view)
      lines = content.splitlines()
      maxLineLength = max([len(line) for line in lines])
      newContent = "".join([ line + ((maxLineLength-len(line)) * " ") + "\n" for line in lines])
      self.view.replace(edit,getViewRegion(self.view),newContent)

# Exits whitespace by removing trailing whitespace
class ExitBlockMode(sublime_plugin.TextCommand):
   def run(self,edit):
      content = getViewContent(self.view)
      lines = content.splitlines()
      newContent = "".join([line.rstrip() + "\n" for line in lines])
      self.view.replace(edit,getViewRegion(self.view),newContent)

class AlignAtBlockEnd(sublime_plugin.TextCommand):

   def maxLength(self, edit):
      maxLength = 0
      for region in self.view.sel():
         lineRegions = self.view.split_by_newlines(region);
         fullLineRegions = [self.view.line(r) for r in lineRegions]
         lines = [self.view.substr(r) for r in fullLineRegions]
         maxLength = max(maxLength, max([len(l) for l in lines]))
      return maxLength

   def run(self, edit):

      newSel = []
      maxLength = self.maxLength(edit)

      # place a cursor on every line for editing
      for region in self.view.sel():
         lineRegions = self.view.split_by_newlines(region);
         fullLineRegions = [self.view.line(r) for r in lineRegions]
         lines = [self.view.substr(r) for r in fullLineRegions]
         for r in fullLineRegions:
            newSel.append(r)
      self.view.sel().clear()
      for r in newSel: self.view.sel().add(r)

      # fill shorter lines with whitespace
      for r in self.view.sel():
         content = self.view.substr(r)
         diff = maxLength - len(content)
         newContent = content + (diff * ' ')
         self.view.replace(edit,r,newContent)

      # move cursors to the end of the lines
      newPositions = [ r.end() for r in self.view.sel() ]
      self.view.sel().clear()
      for p in newPositions:
         self.view.sel().add(sublime.Region(p))