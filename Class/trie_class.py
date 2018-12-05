class Node(object):
    def __init__(self, key, data=None):
        self.key = key
        self.data = data
        self.children = {}


class Trie(object):
    def __init__(self):
        self.head = Node(None)

    def create(self, sentences):
        for sentence in sentences:
            for i in range(len(sentence)):
                sub_sentence = sentence[i:]
                curr_node = self.head

                for char in sub_sentence:
                    if char not in curr_node.children:
                        curr_node.children[char] = Node(char)

                    curr_node = curr_node.children[char]

                curr_node.data = sentences[sentence]

    def search(self, prefix):
        curr_node = self.head
        result = []
        sub_trie = None

        for char in prefix:
            if char in curr_node.children:
                curr_node = curr_node.children[char]
                sub_trie = curr_node
            else:
                return list()

        queue = list(sub_trie.children.values())

        while queue:
            curr = queue.pop()
            if curr.data is not None:
                result.append(curr.data)

            queue += list(curr.children.values())

        return list(result)
