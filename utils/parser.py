import yaml
from baseDS import Graph, Generic, Selection, Stratify


def build_adj_matrix():
    pass


def parse_yaml(file_name: str):
    with open(file_name, 'r') as stream:
        yaml_file = yaml.safe_load(stream)

    nodes_dict = yaml_file["graph"]["nodes"]
    print(nodes_dict)
    listNodes = []
    for key in nodes_dict.keys():
        if "type" not in nodes_dict[key] or nodes_dict[key]["type"] == "Generic":
            # print(nodes_dict[key])
            # if nodes_dict[key]["type"] == ""
            nodes_dict[key] = {**nodes_dict[key], **{"name": key}}
            # print(nodes_dict[key])
            generic = Generic.build_object(**nodes_dict[key])
            listNodes.append(generic)

        elif nodes_dict[key]["type"] == "Selection":
            nodes_dict[key] = {**nodes_dict[key], **{"name": key}}
            selection = Selection.build_object(**nodes_dict[key])
            listNodes.append(selection)

        elif nodes_dict[key]["type"] == "Stratify":
            nodes_dict[key] = {**nodes_dict[key], **{"name": key}}
            stratify = Stratify.build_object(**nodes_dict[key])
            listNodes.append(stratify)

    print(listNodes)
    # listNodes = [NodeW, NodeX, NodeZ, NodeY]
    my_graph = Graph("Graph1", listNodes)
    print(my_graph)


if __name__ == "__main__":
    parse_yaml(file_name="testyml.yml")
