from combo.predict import COMBO
#import torch

#print(f"TORCH: {torch.cuda.is_available()}")
# Download Polish model. Change cuda value to use GPU
nlp = COMBO.from_pretrained("polish-herbert-base-ud213", cuda_device=-1)

sentence = nlp("Padał deszcz, więc wróciłem do domu, a potem zjadłem placki i naleśniki.")

print("{:15} {:15} {:10} {:10} {:10}".format('TOKEN', 'LEMMA', 'UPOS', 'HEAD', 'DEPREL'))
for token in sentence[0].tokens:
    print("{:15} {:15} {:10} {:10} {:10}".format(token.text, token.lemma, token.upostag, token.head, token.deprel))

def find_governors(sentence):
    for token in sentence[0].tokens:
        if token.deprel == 'root':
            root_id = token.idx
            governors_ids = [root_id]
            break
    assert len(governors_ids) != 0, "no root found"

    for token in sentence[0].tokens:
        if token.head in governors_ids and token.deprel in ['advcl', 'ccomp', 'xcomp', 'csubj', 'acl', 'conj']:
            governors_ids.append(token.idx)
    return governors_ids

def get_dependencies(sentence, root_id, stop_token_id):
    dependents = [root_id]
    heads = []
    for token in sentence[0].tokens:
        heads.append(token.head)
    heads = set(heads)

    skip = False
    for i, token in enumerate(sentence[0].tokens):
        if not skip:
            if token.idx != root_id and token.head == root_id and token.idx not in stop_token_id:
                if token.upostag not in ["SCONJ", "CCONJ"]:
                    dependents.append(token.idx)
                    if token.idx in heads and token.upostag in ["VERB", "NOUN"]:
                        dependents.extend(get_dependencies(sentence, token.idx, []))
                elif not (token.deprel == "cc" and  sentence[0].tokens[i+1].deprel =="advmod"):
                    dependents.append(token.idx)
                else:
                    skip = True
        else:
            skip = False

    return set(dependents)        

def get_subtrees(sentence, governors_ids):
    subtrees = []
    for id in governors_ids:
        subtree = [sentence[0].tokens[id-1].idx - 1]
        for token in sentence[0].tokens:
            if token.head == id and token.upostag not in ["VERB", "PUNCT", "SCONJ"]:
                subtree.append(token.idx-1)
        subtrees.append(subtree)
    return subtrees 

def visualize(sentence, ids):
    result = ""
    for el in sorted(ids):
        postag = sentence[0].tokens[el-1].upostag
        head = sentence[0].tokens[el-1].head
        if  postag != "AUX":
                result += " "
        if  postag not in ["PUNCT", "SCONJ"]:
            result += sentence[0].tokens[el-1].text
            
    return result.strip()

#print(visualize(sentence, get_dependencies(sentence, 1, [5])))
#print(visualize(sentence, get_dependencies(sentence, 5, [])))


govs = sorted(find_governors(sentence))
#print(govs)
print("##########")
for gov in govs:
    #print(get_dependencies(sentence, gov, govs))
    print(visualize(sentence, get_dependencies(sentence, gov, govs)))

#print(get_subtrees(sentence, find_governors(sentence)))

