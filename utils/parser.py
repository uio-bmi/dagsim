import yaml
from baseDS import Graph, Generic, Selection, Stratify


def build_adj_matrix():
    pass


def parse_yaml(file_name: str):
    with open(file_name, 'r') as stream:
        yaml_file = yaml.safe_load(stream)

    all_str = ""

    # print(yaml_file)
    listofnodes = "["
    nodes_dict = yaml_file["graph"]["nodes"]
    # print(nodes_dict)
    for key in nodes_dict.keys():
        listofnodes += key + ", "
        empt = ""
        empt += key + ' = Generic(name="' + key + '"'
        empt += ", function=" + nodes_dict[key]['function']
        if "arguments" in nodes_dict[key]:
            empt += ", arguments=" + str(nodes_dict[key]['arguments'])
        if "plates" in nodes_dict[key]:
            empt += ', plates="' + nodes_dict[key]['plates'] + '"'
        empt += ")"
        # print(empt)

        all_str += empt + "\n"

    listofnodes = listofnodes[:-2] + "]\n"
    all_str += "listNodes = " + listofnodes
    all_str += 'my_graph = Graph("Graph1", listNodes)'

    # print(listofnodes)
    print(all_str)


    # listNodes = [NodeW, NodeX, NodeZ, NodeY]
    # my_graph = Graph("Graph1", listNodes)


if __name__ == "__main__":
    parse_yaml(file_name="testyml.yml")
