p1 = ['A']
p2 = ['A', 'B']
p3 = ['C']
p4 = ['A', 'B', 'D', 'E', 'F', 'G', 'H', 'I']
p5 = ['D', 'E']
p6 = ['B']
p7 = ['G', 'H', 'I']

listPlates = [p1, p2, p3, p4, p5, p6, p7]
listLabels = ["p1", "p2", "p3", "p4", "p5", "p6", "p7"]
subs_dict = {i: "subgraph cluster_" + str(i) + " {" + ", ".join(listPlates[i - 1]) + ";\n label=" + listLabels[i - 1]
             for i in
             range(1, len(listPlates) + 1)}


# elem = ['A', 'B', 'D', 'E', 'F']
# large_list = [['A'], ['A', 'B'], ['C'], ['B'], ['E', 'D']]

def find_order(list_of_plates: list):
    resDict = {k: [] for k in range(1, len(list_of_plates) + 1)}
    for plate in list_of_plates:
        if len(plate) != 1:
            checkList = [inPlate for inPlate in list_of_plates if len(inPlate) < len(plate)]
            for inPlate in checkList:
                if set(inPlate).issubset(set(plate)):
                    resDict[list_of_plates.index(plate) + 1].append(list_of_plates.index(inPlate) + 1)
    return resDict


def process_dict(redun_dict: dict):
    innder_plateIdxs = set([item for sublist in my_dict.values() for item in sublist])
    for plate in innder_plateIdxs:
        keysPlate = [key for key in redun_dict.keys() if plate in my_dict[key]]
        if len(keysPlate) == 1:
            continue
        # print("plate", plate)
        # print("before", keysPlate)
        for childPlate in keysPlate:
            for parentPlate in keysPlate:
                if childPlate in redun_dict[parentPlate]:
                    # keysPlate.remove(childPlate)
                    redun_dict[parentPlate].remove(plate)
            if len(keysPlate) == 1:
                break
        # print("after", keysPlate)
    # print(redun_dict)
    return redun_dict


def transform(my_dict, root_plates, subs_dict):
    empL = ""
    lvl = 0

    def prt2(my_dict, root_plates):
        nonlocal empL, lvl, subs_dict
        for idx, root in enumerate(root_plates):
            empL = empL + subs_dict[root] + "\n"
            if not my_dict[root]:
                if idx == (len(root_plates) - 1):
                    lvl -= 1
                    empL = empL + "}"
            else:
                lvl += 1
                prt2(my_dict, my_dict[root])
                empL = empL[:-1]
            empL = empL + "}"

    prt2(my_dict, root_plates)
    return empL


def find_roots(my_dict):
    root_plates = list(range(1, len(my_dict.keys()) + 1))
    # print(root_plates)
    for key in my_dict.keys():
        for val in my_dict[key]:
            root_plates.pop(root_plates.index(val))
    return root_plates


my_dict = find_order(listPlates)
print(my_dict)

my_dict = process_dict(my_dict)
print(my_dict)

root_plates = find_roots(my_dict)

empL = transform(my_dict, root_plates, subs_dict)

print(empL)


def get_plate_dot(plate_embedding):
    subs_dict = {
        i: "subgraph cluster_" + str(i) + " {" + ", ".join(plate_embedding[i][1]) + ';\n label="' + plate_embedding[i][0] + '"'
        for i in range(1, len(plate_embedding.keys()))}
    ordered_dict = find_order([plate_embedding[i][1] for i in range(1, len(plate_embedding.keys()))])
    processed_dict = process_dict(ordered_dict)
    root_plates = find_roots(processed_dict)
    dot_string = transform(processed_dict, root_plates, subs_dict)
    return dot_string
# # default transform
# def transform(my_dict, root_plates):
#     empL = ""
#     lvl = 0
#
#     def prt2(my_dict, root_plates):
#         nonlocal empL, lvl
#         for idx, root in enumerate(root_plates):
#             empL = empL + str(root) + "{"  # subs_dict[root] + "\n"
#             if not my_dict[root]:
#                 if lvl != 0:
#                     if idx == (len(root_plates) - 1):
#                         lvl -= 1
#                         empL = empL + "}"
#             else:
#                 # empL = empL + "{"
#                 lvl += 1
#                 prt2(my_dict, my_dict[root])
#                 empL = empL[:-1]
#             empL = empL + "}"
#
#     prt2(my_dict, root_plates)
#     empL = empL[:-1]
#     return empL
