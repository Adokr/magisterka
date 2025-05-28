import networkx as nx
from combo.predict import COMBO
import spacy
import matplotlib.pyplot as plt

TAGS = {'advcl', 'ccomp', 'csubj', 'parataxis:insert', 'parataxis:obj', 'acl:relcl', 'root'}
VERB_TAGS = {'conj'}

def find_governors(tokens, needRoot, tokensUnchanged):
    if needRoot:
        governors = [token.idx for token in tokens if token.deprel=='root']
        assert len(governors) != 0, "no root found"
    else:
        governors = [tokens[0].idx]

    for i, token in enumerate(tokens):
        if token.head in governors:
            if token.deprel in TAGS:
                governors.append(token.idx)

            elif token.upostag == "VERB" and token.deprel in VERB_TAGS:
                governors.append(token.idx)
            elif token.upostag == "ADJ" and token.deprel in VERB_TAGS and tokensUnchanged[token.head-1].upostag != "ADJ":
                governors.append(token.idx)
            governors.extend(find_governors(tokens[i:], False, tokensUnchanged))
            #else:
                #print(f"TOKENS: {tokens[i:]}")
               # lol = find_governors(tokens[i:], False, tokensUnchanged)
                #print(lol)
               # governors.extend(lol)
    #print(governors_ids)
    #print(f"IDS {governors_ids}")
   # if governors_ids != []:
    #    texts = [tokens[id-1].text for id in governors_ids]
   
    if governors == [tokens[0].idx] and tokens[0].deprel != 'root':
        print(f"GOVS {governors}")
        governors = []
    return governors#, texts


def get_dependencies(tokens, rootId, stopTokenIds, ugh):
    dependents = [rootId]
    heads = set([token.head for token in tokens])
    allTokens = tokens
    x = 0
    skip_next = False

    if len(ugh)-len(stopTokenIds) >= 2:
        x = ugh[len(ugh)-len(stopTokenIds)-2]
        
   
    stopTokenIds = [x for x in stopTokenIds if x > rootId]

    if stopTokenIds == []:
        stopTokenId = 100000000
    else:
        stopTokenId = stopTokenIds[0]

    #tokens = tokens[x:stopTokenId]

    for i, token in enumerate(tokens):
        if skip_next:
            skip_next = False
            continue
        
        if token.idx == rootId or token.idx >= stopTokenId:
            continue

        if token.head == rootId:
            if token.upostag not in ["SCONJ", "CCONJ", "X"]:
                dependents.append(token.idx)
                if token.idx in heads and token.upostag in ["VERB", "NOUN", "ADJ", "PROPN", "PRON"]:
                    dependents.extend(get_dependencies(allTokens, token.idx, stopTokenIds, ugh))
            elif token.deprel in {"cc", "advmod"}:
                if tokens[i+1].deprel in {"cc", "advmod"}:
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
            if tokens[el-1].upostag not in {"PUNCT", "SCONJ"}:#tokens[el-1].text not in {",", ".", "-"}:
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
    for gov in sorted(governors_ids):
        spans.append(get_dependencies(tokens, gov, governors_ids, governors_ids))
    
    return spans
    #print("##########")
    #for i, gov in enumerate(sorted(governors_ids)):
    #    print(visualize(tokens, get_dependencies(tokens, gov, governors_ids), i+1))

def main():
    with open("tekst.txt", "r", encoding='utf-8') as f: #usunąłem kropki przy skrótach al. i ul., oraz usunąłem spację przed jednym z wielokropków
        text = f.read()
    
    nlp_blank = spacy.blank("pl")
    combo = COMBO.from_pretrained("polish-herbert-base-ud213")

    parsedText = combo(text)
    dependencyTrees = []
    for sentence in parsedText[12:13]:
        graph = nx.DiGraph()
        graph.add_nodes_from([(token.idx, token.text) for token in sentence.tokens])
        graph.add_edges_from([((sentence.tokens[token.head-1].idx, sentence.tokens[token.head-1].text), (token.idx, token.text)) for token in sentence.tokens])
        graph.remove_edge((sentence.tokens[-1].idx, sentence.tokens[-1].text), (sentence.tokens[sentence.tokens[-1].head-1].idx, sentence.tokens[sentence.tokens[-1].head-1].text))
        dependencyTrees.append(graph)
        
        govs = find_governors(sentence.tokens, True, sentence.tokens)
        print([(gov, sentence.tokens[gov-1].text) for gov in govs])
        better = set([ids for ids in govs if sentence.tokens[ids-1].deprel in TAGS or sentence.tokens[ids-1].deprel in VERB_TAGS])
        print([(gov, sentence.tokens[gov-1].text) for gov in better])
    

        #nx.draw_networkx(graph,#.subgraph([1, 2, 3, 4, 5]),
              #           with_labels=True, node_color='lightblue', edge_color='gray', arrows=True)
                         #labels={token.idx:token.text for token in sentence.tokens})
        #plt.show()
        

if __name__== "__main__":
    main()
