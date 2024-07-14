import queue
import bitstring


class HuffmanNode:
    def __init__(self, weight, char):
        self.weight = weight
        self.char = char

    def __lt__(self, other):
        return self.weight < other.weight


class HuffmanTree(HuffmanNode):
    def __init__(self, left, right):
        super().__init__(left.weight + right.weight, left.char + right.char)
        self.left = left
        self.right = right


def build_tree(alphabet):
    q = queue.PriorityQueue()
    for char, weight in alphabet.items():
        q.put(HuffmanNode(weight, char))
    while q.qsize() > 1:
        q.put(HuffmanTree(q.get(), q.get()))
    return q.get()


def get_codes(tree, code=0):
    if isinstance(tree, HuffmanTree):
        return (get_codes(tree.left, code << 1) |
                get_codes(tree.right, (code << 1) ^ 1))
    return {tree.char: code}


def encode(s, weights):
    codes = get_codes(build_tree(weights))
    arr = bitstring.BitArray()
    for c in s:
        val = codes[c]
        arr.append(bitstring.Bits(uint=val, length=max(val.bit_length(), 1)))
    return arr.tobytes()


if __name__ == '__main__':
    print(get_codes(build_tree({'a': 4, 'b': 7, 'c': 4})))