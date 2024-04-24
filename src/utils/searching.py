import json

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
        return self._collect_entries(node, prefix)

    def _collect_entries(self, node, prefix):
        result = []
        if node.is_end_of_word:
            result.append(prefix)
        for char, child_node in node.children.items():
            result.extend(self._collect_entries(child_node, prefix + char))
        return result

class TreeNode:
    def __init__(self, name, parent=None):
        self.name = name
        self.children = {}
        self.trie = Trie()
        self.parent = parent

    def add_child(self, name, child_node):
        self.children[name] = child_node

    def get_child(self, name):
        return self.children.get(name)

    def get_possible_values(self, prefix):
        return self.trie.search(prefix)

    def insert_into_trie(self):
        for child in self.children.values():
            self.trie.insert(child.name)


class TaxonomyTree:
    def __init__(self):
        self.root = TreeNode("root")

    def add_taxon(self, taxon_path):
        current_node = self.root
        for taxon in taxon_path:
            if not current_node.get_child(taxon):
                new_node = TreeNode(taxon, parent=current_node)
                current_node.add_child(taxon, new_node)
            current_node = current_node.get_child(taxon)
            current_node.insert_into_trie()

    def get_parents(self, taxon_name):
        node = self._find_node(self.root, taxon_name)
        if node is None:
            return None
        parents = []
        while node.parent is not None:
            parents.append(node.parent.name)
            node = node.parent
        parents.reverse()  # Reverse the list to get the path from the root to the node
        return parents

    def _find_node(self, node, taxon_name):
        if node.name == taxon_name:
            return node
        for child in node.children.values():
            result = self._find_node(child, taxon_name)
            if result is not None:
                return result
        return None

    def get_possible_values(self, current_path, prefix=""):
        current_node = self.root
        for taxon in current_path:
            current_node = current_node.get_child(taxon)
            if current_node is None:
                return []
        return current_node.get_possible_values(prefix)

    def prefix_search(self, level, prefix):
        if level < 0 or level > 4:
            raise ValueError("Invalid level: " + str(level))
        results = []
        self._prefix_search_recursive(self.root, level, prefix, results, 0)
        return results

    def _prefix_search_recursive(self, node, level, prefix, results, current_level):
        if current_level == level - 1:
            results.extend(node.trie.search(prefix))
        if current_level < level - 1:
            for child in node.children.values():
                self._prefix_search_recursive(child, level, prefix, results, current_level + 1)

def init_taxonomy(taxonomy_dir):
    taxonomy_tree = TaxonomyTree()

    with open(taxonomy_dir, "r") as f:
        taxonomy_dict = json.load(f)
    for entry in taxonomy_dict:
        taxonomy_tree.add_taxon([
            entry['order'],
            entry['family'],
            entry['genus'],
            entry['species']
        ])
    return taxonomy_tree

if __name__ == "__main__":
    taxonomy_dir = "resources/taxonomy/taxonomy.json"

    taxonomy = init_taxonomy(taxonomy_dir)

    print(taxonomy.get_parents("Dasyleptus brongniarti"))
    current_path = ['Archaeognatha']
    prefix = "M"
    print(taxonomy.get_possible_values(current_path, prefix))

    f_genera = taxonomy.prefix_search(4, "Da")
    for genus in f_genera:
        print(genus, taxonomy.get_parents(genus))
