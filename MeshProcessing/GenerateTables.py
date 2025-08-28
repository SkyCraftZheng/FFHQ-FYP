lm_labels = ["right tear duct", "top of head", "left tear duct", "tip of nose", "left mouth corner", "right mouth corner",
    "chin", "top lip", "bottom lip",
    "right top eyelid 1", "right top eyelid 2", "left top eyelid 1", "left top eyelid 2",
    "right bottom eyelid", "left bottom eyelid", "right ear", "left ear",
    "middle brow bridge", "right brow 1", "right brow 2", "left brow 1", "left brow 2",
    "right eye corner", "left eye corner"]
UMA_idx = [472, 682, 134, 709, 307, 646,
    713, 702, 696,
    478, 476, 138, 140,
    482, 144, 381, 43,
    717, 599, 559, 261, 221,
    475, 137]
FFHQ_idx = [4587, 10040, 2042, 703, 7771, 12908,
    676, 735, 706,
    18851, 3744, 1186, 1204,
    3759, 1214, 3039, 413,
    680, 11962, 3582, 6797, 6892,
    14123, 2099]
weights = [0.016, 0.4, 0.016, 0.1, 0.03, 0.03,
    0.13, 0.05, 0.05,
    0.02, 0.01, 0.02, 0.01,
    0.02, 0.02, 0.09, 0.09,
    0.2, 0.04, 0.031, 0.4, 0.031,
    0.021, 0.021]

with open("table1.txt", 'w') as output:
    output.write("\n\\begin{table}\n\\centering\n\\begin{tabular}{|c|c|c|c|c|}\n\\hline\nLandmark & UMA index & FFHQ index & weight \\\\ \\hline\n")
    for label, UMA_id, FFHQ_id, weight in zip(lm_labels, UMA_idx, FFHQ_idx, weights):
        output.write("{} & {} & {} & {} \\\\\n".format(str(label), str(UMA_id), str(FFHQ_id), str(weight)))
    output.write("\\hline\n\\end{tabular}\n\\caption{}\n\\end{table}")

cut_labels = ["neck right", "neck right back", "neck back", "neck left back", "neck left", "neck front"]
cut_UMA_idx = [468, 470, 689, 132, 130, 690] 
cut_idx = [4683, 4800, 2135, 9567, 2186, 2155]
neck_weights = [0.05, 0.04, 0.2, 0.04, 0.05, 0.2]

with open("table2.txt", 'w') as output:
    output.write("\n\\begin{table}\n\\centering\n\\begin{tabular}{|c|c|c|c|c|}\n\\hline\nCut labels & UMA index & FFHQ index & weight \\\\ \\hline\n")
    for label, UMA_id, FFHQ_id, weight in zip(cut_labels, cut_UMA_idx, cut_idx, neck_weights):
        output.write("{} & {} & {} & {} \\\\\n".format(str(label), str(UMA_id), str(FFHQ_id), str(weight)))
    output.write("\\hline\n\\end{tabular}\n\\caption{}\n\\end{table}")

DNA_labels = ["Cheek Position", "Cheek Size", "Chin Position", "Chin Pronounced", "Chin Size",
              "Ears Position", "Ears Rotation", "Ears Size",
              "Eye Rotation", "Eye Size", "Eye Spacing",
              "Forehead Position", "Forehead Size", "Head Width",
              "Jaws Postion", "Jaws Size", "Lips Size", "Mandible Size", "Mouth Size",
              "Neck Thickness", "Nose Curve", "Nose Flatten", "Nose Inclination",
              "Nose Position", "Nose Pronounced", "Nose Size", "Nose Width"]
DNA_values = [0.41568, 0.60392, 0.14509, 0.54901, 0.66274,
              0.13333, 0.56076, 0.77647,
              0.19215, 1.0, 0.58039,
              0.48235, 0.63529, 0.63137,
              0.14117, 0.36470, 0.40784, 0.57254, 0.55686,
              0.64313, 0.75686, 0.65490, 0.38039,
              0.61176, 0.54901, 0.50196, 0.33333]

with open("table3.txt", 'w') as output:
    output.write("\n\\begin{table}\n\\centering\n\\caption{}\n\\begin{tabular}{|c|c|}\n\\hline\nDNA label & DNA Value \\\\ \\hline\n")
    length = len(DNA_labels)
    for i in range(length//2):
        output.write("{} & {} \\\\\n".format(str(DNA_labels[i]), str(DNA_values[i])))
    output.write("\\hline\n\\end{tabular}\n\\begin{tabular}{|c|c|}\n\\hline\nDNA label & DNA Value \\\\ \\hline\n")
    for i in range(length//2, length):
        output.write("{} & {} \\\\\n".format(str(DNA_labels[i]), str(DNA_values[i])))
    output.write("\\hline\n\\end{tabular}\n\\end{table}")