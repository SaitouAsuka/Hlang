class HLangSyntaxError(ValueError):

    def __init__(self, message, filename, lineno, colno, source=None) -> None:
        self.message_ = message
        self.filename_ = filename
        self.lineno_ = lineno if lineno > 0 else 1
        self.colno_ = colno if colno > 0 else 1
        self.source_ = source

    def __str__(self):
        msg = f'File "{self.filename_}", line {self.lineno_}:{self.colno_}, {self.message_}'
        if self.source_:
            line = self.source_[self.lineno_ - 1]
            col = ' '* (self.colno_ - 1) + "^"
            msg = f'{msg}\n{line}\n{col}'
        return msg