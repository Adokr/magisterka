from combo.predict import COMBO
#import torch

#print(f"TORCH: {torch.cuda.is_available()}")

TAGS = {'advcl', 'ccomp', 'csubj', 'acl', 'conj'}

# Download Polish model. Change cuda value to use GPU
'''nlp = COMBO.from_pretrained("polish-herbert-base-ud213", cuda_device=-1)
sentence = nlp("Padał deszcz, więc wróciłem do domu, a potem zjadłem placki i naleśniki.")

print("{:15} {:15} {:10} {:10} {:10}".format('TOKEN', 'LEMMA', 'UPOS', 'HEAD', 'DEPREL'))
for token in sentence[0].tokens:
    print("{:15} {:15} {:10} {:10} {:10}".format(token.text, token.lemma, token.upostag, token.head, token.deprel))'''

def find_governors(tokens):
    governors_ids = [token.idx for token in tokens if token.deprel=='root']
    assert len(governors_ids) != 0, "no root found"

    for token in tokens:
        if token.head in governors_ids and token.deprel in TAGS:
            governors_ids.append(token.idx)
    print(f"IDS {governors_ids}")
    return governors_ids


def get_dependencies(tokens, root_id, stop_token_id):
    dependents = [root_id]
    heads = set([token.head for token in tokens])

    skip_next = False

    for i, token in enumerate(tokens):
        if skip_next:
            skip_next = False
            continue
        
        if token.idx == root_id or token.idx in stop_token_id:
            continue

        if token.head == root_id:
            if token.upostag not in ["SCONJ", "CCONJ"]:
                dependents.append(token.idx)
                if token.idx in heads and token.upostag in ["VERB", "NOUN"]:
                    dependents.extend(get_dependencies(tokens, token.idx, []))
            elif not (token.deprel == "cc" or tokens[i+1].deprel =="advmod"):
                dependents.append(token.idx)
            else:
                skip_next = True
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

def visualize(tokens, ids, unit_count):
    result = [f"Unit {unit_count}:"]
    for el in sorted(ids):
        postag = tokens[el-1].upostag
        if  postag not in ["AUX", "PUNCT", "SCONJ"]:
            result.append(" ")
        if  postag not in ["PUNCT", "SCONJ"]:
            result.append(tokens[el-1].text)
    return ''.join(result).strip()

def remove_punct(tokens, spans):
    new_spans = []
    for span in spans:
        new_span = []
        for el in span:
            if tokens[el-1].upostag not in {"PUNCT", "SCONJ"}:
                new_span.append(el-1)
        new_spans.append(new_span)
    return new_spans

def find_spans(tokens):
    spans = []
    governors_ids = [token.idx for token in tokens if token.deprel=='root']
    assert len(governors_ids) != 0, "no root found"

    for token in tokens:
        if token.head in governors_ids and token.deprel in TAGS:
            governors_ids.append(token.idx)
    print(f"GOVS: {governors_ids}")
    for gov in sorted(governors_ids):
        spans.append(get_dependencies(tokens, gov, governors_ids))
    
    return spans
    #print("##########")
    #for i, gov in enumerate(sorted(governors_ids)):
    #    print(visualize(tokens, get_dependencies(tokens, gov, governors_ids), i+1))


