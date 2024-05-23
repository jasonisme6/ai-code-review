from opencv.detect_code_content import remove_hint_from_code_line


if __name__ == "__main__":
    str = " self.rnn.add_module(name: 'blstm', BLSTM(3 * 3 * 512, hidden_unit: 128))\n"
    print(remove_hint_from_code_line(str, 2))