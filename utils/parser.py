import yaml
from baseDS import Graph, Generic, Selection, Stratify


def build_adj_matrix():
    pass


def parse_yaml(file_name: str):
    with open(file_name, 'r') as stream:
        yaml_file = yaml.safe_load(stream)


if __name__ == "__main__":
    parse_yaml(file_name="testyml.yml")
