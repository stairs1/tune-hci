class Defaults():
    OUTPUT_FUNC = lambda *_: None

class Logger():
    def __init__(self, output=None, log_len=10):
        self.output = output or Defaults.OUTPUT_FUNC
        self.log = []
        self.log_len = log_len

    def input_to_log(self, *args):
        self.log.append(args)
        self.log = self.log[-self.log_len:]
        self.output(*args)

class PrintLogger(Logger):
    def input_to_log(self, *args):
        print(self.log)
        super().input_to_log(*args)