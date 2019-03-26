from translator import *


class FunctionEncoder(object):

    def __init__(self, abi):
        super(FunctionEncoder, self).__init__()

        self.function_data = {}

        if abi.get('type', None) != 'function':
            raise ValueError('The abi type is must be function')

        if 'signature' not in abi:
            raise ValueError('The abi must have signature field')

        normalized_name = normalize_name(abi['name'])
        encode_types = [
            element['type']
            for element in abi.get('inputs', [])
        ]
        decode_types = [
            element['type']
            for element in abi.get('outputs', [])
        ]
        self.function_data[normalized_name] = {
            'prefix': int(abi.get('signature', '0x0'), 16),
            'encode_types': encode_types,
            'decode_types': decode_types
        }

    def encode_function(self, function_name, args):
        """ Return the encoded function call.

        Args:
            function_name (str): One of the existing functions described in the
                contract interface.
            args (List[object]): The function arguments that wll be encoded and
                used in the contract execution in the vm.

        Return:
            bin: The encoded function name and arguments so that it can be used
                 with the evm to execute a funcion call, the binary string follows
                 the Ethereum Contract ABI.
        """
        if function_name not in self.function_data:
            raise ValueError('Unkown function {}'.format(function_name))

        function = self.function_data[function_name]

        function_selector = zpad(encode_int(function['prefix']), 4)
        arguments = encode_abi(function['encode_types'], args)

        return '0x' + encode_hex(function_selector + arguments)


if __name__ == "__main__":
    abi = {
        "constant": False,
        "inputs": [
          {
              "name": "_id",
              "type": "uint256"
          }
        ],
        "name": "finish",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
        "signature": "0xd353a1cb"
    }
    r = FunctionEcoder(abi).encode_function(abi['name'], [1])
    print(r == '0xd353a1cb0000000000000000000000000000000000000000000000000000000000000001')
