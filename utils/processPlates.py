def find_order(list_of_plates: list):
    """ A function that finds which plates are sub-plates of other plates.

    Args:
        list_of_plates (list): A list of lists, where each sublist contains the nodes found in the plate with
            the corresponding index.

    Returns:
        dict: A dictionary of the sub-plates, if any, of each plate.

    """
    resDict = {k: [] for k in range(1, len(list_of_plates) + 1)}
    for plate in list_of_plates:
        if len(plate) != 1:
            checkList = [inPlate for inPlate in list_of_plates if len(inPlate) < len(plate)]
            for inPlate in checkList:
                if set(inPlate).issubset(set(plate)):
                    resDict[list_of_plates.index(plate) + 1].append(list_of_plates.index(inPlate) + 1)
    return resDict


def process_dict(redun_dict: dict):
    """ A function that finds the direct child plates, if any, of each plate.

    Args:
        redun_dict (dict): A dictionary containing the, possibly redundant, sub-plates of each plate.

    Returns:
        dict: A dictionary of the direct child plates, if any, of each plate.

    """
    innder_plateIdxs = set([item for sublist in redun_dict.values() for item in sublist])
    for plate in innder_plateIdxs:
        keysPlate = [key for key in redun_dict.keys() if plate in redun_dict[key]]
        if len(keysPlate) == 1:
            continue
        for childPlate in keysPlate:
            for parentPlate in keysPlate:
                if childPlate in redun_dict[parentPlate]:
                    redun_dict[parentPlate].remove(plate)
            if len(keysPlate) == 1:
                break
    return redun_dict


def transform(processed_dict, root_plates, subs_dict):
    """ A function that generates the .dot string for all the plates in the graph, in the correct order.

    Args:
        processed_dict (dict): A dictionary of the direct child plates, if any, of each plate.
        root_plates (list): A list of the root plates.
        subs_dict (dict): A dictionary of strings to define each plate in .dot format.

    Returns:
        string: A string defining all the plates and their nodes, in .dot format.

    """
    dot_string = ""
    level = 0

    def plate_string(processed_dict, root_plates):
        nonlocal dot_string, level, subs_dict
        for idx, root in enumerate(root_plates):
            dot_string = dot_string + subs_dict[root] + "\n"
            if not processed_dict[root]:
                if idx == (len(root_plates) - 1):
                    level -= 1
                    dot_string = dot_string + "}"
            else:
                level += 1
                plate_string(processed_dict, processed_dict[root])
                dot_string = dot_string[:-1]
            dot_string = dot_string + "}"

    plate_string(processed_dict, root_plates)
    return dot_string[0:-1]


def find_roots(processed_dict):
    """ A function that finds the plates that are not contained in other plates.

    Args:
        processed_dict (dict): A dictionary of the direct child plates, if any, of each plate.

    Returns:
        list: A list of the root plates.

    """
    root_plates = list(range(1, len(processed_dict.keys()) + 1))
    for key in processed_dict.keys():
        for val in processed_dict[key]:
            root_plates.pop(root_plates.index(val))
    return root_plates


def get_plate_dot(plate_embedding):
    """ A wrapper function that generates the part of the .dot string corresponding to the plates.

    Args:
        plate_embedding (dict): A dictionary containing the label and nodes of each plate.

    Returns:
        str: A string defining the plates in .dot format.

    """
    subs_dict = {
        i: "subgraph cluster_" + str(i) + " {" + ", ".join(plate_embedding[i][1]) + ';\n label="' +
           plate_embedding[i][0] + '"' for i in range(1, len(plate_embedding.keys()))}
    ordered_dict = find_order([plate_embedding[i][1] for i in range(1, len(plate_embedding.keys()))])
    processed_dict = process_dict(ordered_dict)
    root_plates = find_roots(processed_dict)
    dot_string = transform(processed_dict, root_plates, subs_dict)
    return dot_string


if __name__ == "__main__":
    sample_plate_embedding = {0: (None, ['Prior', 'Node4']), 1: ('plate_1', ['Node1', 'Node2']),
                              2: ('plate_2', ['Node5', 'Node1', 'Node2'])}
    # Note that the 0th plate is excluded from the .dot string generation.
    print(get_plate_dot(sample_plate_embedding))
