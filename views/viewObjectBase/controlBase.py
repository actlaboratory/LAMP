#controlBase for ViewCreator
#Copyright (C) 2019-2020 Hiroki Fujii <hfujii@hisystron.com>

class controlBase():
    def AcceptsFocusFromKeyboard(self):
        if self.IsEnabled(): return self.focusFromKbd
        else: False
