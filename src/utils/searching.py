class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        return self._collect_species(node, prefix)

    def _collect_species(self, node, prefix):
        result = []
        if node.is_end_of_word:
            result.append(prefix)
        for char, child_node in node.children.items():
            result.extend(self._collect_species(child_node, prefix + char))
        return result

# Example usage:
trie = Trie()
# Populate the trie with insect species names
insect_species = [...]  # Your list of 20k insect species names
for species in insect_species:
    trie.insert(species)

# Perform search operation
search_query = "your_search_query"
matching_species = trie.search(search_query)
print("Matching species:")
for species in matching_species:
    print(species)
