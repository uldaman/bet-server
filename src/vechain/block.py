from request import Request, get


class Block(object):

    def __init__(self, endpoint: str):
        self.blocks = Request(endpoint).blocks
        super(Block, self).__init__()

    def best_num(self):
        blk = self.blocks('best').make_request(get)
        return blk['number']


if __name__ == "__main__":
    block = Block('https://sync-testnet.vechain.org')
    print(block.best_num())
