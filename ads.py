import networkx as nx
from combo.predict import COMBO
import spacy
from spacy.tokens import Doc, Span
import matplotlib.pyplot as plt

TAGS = {'advcl', 'ccomp', 'csubj', 'parataxis:insert', 'parataxis:obj', 'acl:relcl', 'root'} # ccomp
VERB_TAGS = {'conj', 'acl:relcl'}
PUNCT_TAGS =  {",", ".", ";", ":", "-", '"'}
MAX_UNITS = 60
COLORS_NAMES = ["turquoise", " lightcoral", "mediumorchid", 
                "sandybrown", "palegreen", "deepskyblue",
                "hotpink", "teal", "peru", "fuchsia", 
                "maroon", "seagreen", "lightsteelblue", "navajowhite",
                "crimson", "olive", "k", "plum", "wheat", "royalblue",
                "turquoise", " lightcoral", "mediumorchid", 
                "sandybrown", "palegreen", "deepskyblue",
                "hotpink", "teal", "peru", "fuchsia", 
                "maroon", "seagreen", "lightsteelblue", "navajowhite",
                "crimson", "olive", "k", "plum", "wheat", "royalblue",
                "turquoise", " lightcoral", "mediumorchid", 
                "sandybrown", "palegreen", "deepskyblue",
                "hotpink", "teal", "peru", "fuchsia", 
                "maroon", "seagreen", "lightsteelblue", "navajowhite",
                "crimson", "olive", "k", "plum", "wheat", "royalblue"]

def find_governors_from_graph(graph, subroot):
    if subroot == None:
        root = [nodeID for nodeID in graph.nodes if graph.nodes[nodeID]['token'].deprel == 'root'][0]
        governors = [root]
    else:
        root = subroot
        governors = []

    for successor in graph.successors(root):
        token = graph.nodes[successor]['token']
        if token.deprel in TAGS:
            governors.append(token.idx)
        elif token.upostag == "VERB" and token.deprel in VERB_TAGS:
            governors.append(token.idx)
        elif token.upostag == "ADJ" and token.deprel in VERB_TAGS and graph.nodes[root]['token'].upostag != "ADJ":
            governors.append(token.idx)
        governors.extend(find_governors_from_graph(graph, successor))
    return governors

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

def sentence_to_graph(sentence):
    G = nx.DiGraph()
    for token in sentence.tokens:
        G.add_node(token.idx, token=token)   

    for token in sentence.tokens:
        if token.head != 0:
            G.add_edge(token.head, token.idx, label=token.deprel)
    
    #for node in G.nodes:
      #  print(f"NODES: {node}")

    return G

def getSubtree(graph, head):
    dependents = [head]
        

    return None

def getSpans(graph, spanHeads):
    spans = []
    textSpans = []
    for head in spanHeads:
        span = nx.descendants(graph, head)
        span.add(head)
        span = {nodeID for nodeID in graph.nodes if (nodeID in span)}# and graph.nodes[nodeID]['token'].deprel not in {"mark", "punct", "cc"})}
        spans.append(span)
    spans = sorted(spans, key=len, reverse=True)
    proper = []

    for i in range(len(spans)):
        span = spans[i]
        for j in range(i+1, len(spans)):
            span -= spans[j]
        '''if i < len(spans)-1:
            span = spans[i]-spans[i+1]
        elif proper != []:
            span = spans[i] - proper[0]
        elif spans[i] != []: #czy to działa?
            span = spans[i]'''
       # print(f"\nI : {i},\t {span}\n")
        if span:
            proper.append(span)
    #print(f"PROPER {proper}")
    proper = sorted(proper, key=min)
    for span in proper:
        textSpans.append(" ".join([graph.nodes[nodeID]['token'].text for nodeID in graph.nodes if nodeID in span]))
    return textSpans, proper

def check_continuity(my_list):
    return all(a+1==b for a, b in zip(my_list, my_list[1:]))

def removeSingleTokens(my_list):
    new_list = []
    for el in my_list:
        if not(el+1 not in my_list and el-1 not in my_list):
            new_list.append(el)
    return new_list

def findSplit(my_list):
    splits = []
    for a, b in zip(my_list, my_list[1:]):
        if a+1!=b:
            splits.append((a, b))
    print(f"split {splits}")
    return splits

def main():
    with open("tekst.txt", "r", encoding='utf-8') as f: #usunąłem kropki przy skrótach al. i ul., oraz usunąłem spację przed jednym z wielokropków
        text = f.read()
    
    nlp_blank = spacy.blank("pl")
    combo = COMBO.from_pretrained("polish-herbert-base-ud213")
    docs = []
    parsedText = combo(text)
    dependencyTrees = []
    for i, sentence in enumerate(parsedText):

        graph = sentence_to_graph(sentence)
        dependencyTrees.append(graph)
        governors = sorted(find_governors_from_graph(graph, None))
        textSpans, tokenSpans = getSpans(graph, governors)

        words = [token.text for token in sentence.tokens]
        doc = Doc(nlp_blank.vocab, words=words)
        doc.spans["sc"] = []
        print(f"tokenSpans {tokenSpans}")
        for j, span in enumerate(tokenSpans):
            if check_continuity(list(span)):
                span = {nodeID for nodeID in span if graph.nodes[nodeID]['token'].deprel not in {"mark", "cc"} and graph.nodes[nodeID]['token'].text not in PUNCT_TAGS}
                print(f"span {span}")
                doc.spans["sc"].append(Span(doc, min(span)-1, max(span), f"{j+1}. człon"))
            else:
                span = removeSingleTokens(list(span))
                print(f"discontinuous {span}")
                if check_continuity(list(span)):
                    span = {nodeID for nodeID in span if graph.nodes[nodeID]['token'].deprel  not in {"mark", "cc"} and graph.nodes[nodeID]['token'].text not in PUNCT_TAGS}

                    doc.spans["sc"].append(Span(doc, min(span)-1, max(span), f"{j+1}. człon"))
                else:
                    span = {nodeID for nodeID in span if graph.nodes[nodeID]['token'].deprel  not in {"mark", "cc"}  and graph.nodes[nodeID]['token'].text not in PUNCT_TAGS}

                    splits = findSplit(list(span))
                    print(f"split {splits}")
                    if splits != []:
                        for split in splits:
                            doc.spans["sc"].append(Span(doc, min(span)-1, split[0], f"{j+1}. człon"))
                            doc.spans["sc"].append(Span(doc, split[1]-1, max(span), f"{j+1}. człon"))
                    else:
                        doc.spans["sc"].append(Span(doc, min(span)-1, max(span), f"{j+1}. człon"))
        '''for i, span in enumerate(tokenSpans):
            if check_continuity(list(span)):
                span = {nodeID for nodeID in span if graph.nodes[nodeID]['token'].deprel not in {"mark", "punct"}}
                span = removeSingleTokens(list(span))
                print(f"span1 {span}")
                doc.spans["sc"].append(Span(doc, min(span)-1, max(span), f"{i+1}. człon"))
            else:
                span = removeSingleTokens(list(span))
                splits = findSplit(list(span))
                
                print(f"span2 {span}")
                if splits != []:
                    for split in splits:
                        if split[1]-split[0] > 2:
                            doc.spans["sc"].append(Span(doc, min(span)-1, split[0], f"{i+1}. człon"))
                            doc.spans["sc"].append(Span(doc, split[1]-1, max(span), f"{i+1}. człon"))
                        else:
                            newSpan = Span(doc, min(span)-1, max(span), f"{i+1}. człon")
                            if newSpan not in doc.spans["sc"]:
                                doc.spans["sc"].append(newSpan)
                else:
                     doc.spans["sc"].append(Span(doc, min(span)-1, max(span), f"{i+1}. człon"))'''

        print(f"DOC {doc.spans['sc']}\n")
        docs.append(doc)
       # print(f"DOCS {docs}")
    
    options = {"colors": {key: value for key, value 
                    in zip([f"{i+1}. człon" for i in range(MAX_UNITS)], COLORS_NAMES)}}
    spacy.displacy.serve(docs, style="span", options=options)

    '''govs = find_governors(sentence.tokens, True, sentence.tokens)
        print([(gov, sentence.tokens[gov-1].text) for gov in govs])
        better = set([ids for ids in govs if sentence.tokens[ids-1].deprel in TAGS or sentence.tokens[ids-1].deprel in VERB_TAGS])
        print([(gov, sentence.tokens[gov-1].text) for gov in better])'''
        

if __name__== "__main__":
    main()
