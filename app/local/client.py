from msl.loadlib import Client64


class Client(Client64):

    def __init__(self):
        super(Client, self).__init__(module32='server', host="127.0.0.1", port=None)

    def fsl_command(self, com, doc):
        return self.request32('fsl_command', com, doc)


# class LinearAlgebra(Client64):
#
#     def __init__(self):
#         super(LinearAlgebra, self).__init__(module32='linear_algebra_32.py')
#
#     def __getattr__(self, name):
#         def send(*args, **kwargs):
#             return self.request32(name, *args, **kwargs)
#         return send
