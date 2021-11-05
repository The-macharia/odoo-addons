from msl.loadlib import Server32


class Server(Server32):
    def __init__(self, host, port, **kwargs):
        super(Server, self).__init__('tresdlib.dll', 'windll', host, port)

    def fsl_command(self, com, doc):
        return self.lib.FSL_Command("C:\\ESD", "SIGN", "TSL1900187.txt", "MISC_001_2021.txt", "C:\\ESD")
