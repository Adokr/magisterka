import networkx as nx
from combo.predict import COMBO
import spacy
from spacy.tokens import Doc, Span
import matplotlib.pyplot as plt
import os
import cassis
import html
import re

TAGS = {'advcl', 'ccomp', 'csubj', 'parataxis:insert', 'parataxis:obj', 'acl:relcl', 'root'} # ccomp
VERB_TAGS = {'conj', 'acl:relcl'}
PUNCT =  {",", ".", ";", ":", "-", '"'}
ABBREVIATIONS = {"np.", "itd.", "itp.", "dr.", "prof.", "ul.", "al.", "p.", "sz.", "tzw.", "reż.", "godz.", "min."}
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

def prepareString(text):
    
    cleaned_text = re.sub(r'\s*([,.?!\'])\s*', r'\1 ', text)
    cleaned_text = re.sub(r'(\.\s\.\s\.\s)', '... ', cleaned_text)
    
    new = ""
    skip = False
    quotationOpened = False
    for char in list(cleaned_text):
        if char == '"':
            if quotationOpened:
                new = "".join(list(new[:-1]))
                quotationOpened = False
                skip = False
            else:
                skip = True
                quotationOpened = True
            new += char
        elif not skip:
            new += char
        else:
            skip = False
    
    finalText = []
    for word in new.split():
        if word.lower() not in ABBREVIATIONS:
            finalText.append(word)
        else:
            finalText.append("".join(word)[:-1])
    return " ".join(finalText)

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

def sentence_to_graph(sentence):
    G = nx.DiGraph()
    for token in sentence.tokens:
        G.add_node(token.idx, token=token)   

    for token in sentence.tokens:
        if token.head != 0:
            G.add_edge(token.head, token.idx, label=token.deprel)
    
    #for node in G.nodes:
     #   print(f"NODES: {node, G.nodes[node]['token'], G.nodes[node]['token'].deprel, G.nodes[node]['token'].head }")

    return G

def getSpans(graph, spanHeads):
    spans = []
    properSpans = []
    for head in spanHeads:
        span = nx.descendants(graph, head)
        span.add(head)
        span = {nodeID for nodeID in graph.nodes if (nodeID in span)}# and graph.nodes[nodeID]['token'].deprel not in {"mark", "punct", "cc"})}
        spans.append(span)
    spans = sorted(spans, key=len, reverse=True)

    for i in range(len(spans)):
        span = spans[i]
        for j in range(i+1, len(spans)):
            span -= spans[j]
        if span:
            properSpans.append(span)
    properSpans = sorted(properSpans, key=min)
    
    #textSpans = []
    #for span in properSpans:
     #   textSpans.append(" ".join([graph.nodes[nodeID]['token'].text for nodeID in graph.nodes if nodeID in span]))
    return properSpans

def check_continuity(my_list):
    return all(a+1==b for a, b in zip(my_list, my_list[1:]))

def removeSingleTokens(my_list):
    new_list = []
    if len(my_list) > 2:
        for el in my_list:
            if not(el+1 not in my_list and el-1 not in my_list):
                new_list.append(el)
    else:
        new_list = my_list
    return new_list

def findSplit(my_list):
    splits = []
    for a, b in zip(my_list, my_list[1:]):
        if a+1!=b:
            splits.append((a, b))
    return splits

def prepareDoc(parsedText, nlp):
    docs = []
    dependencyTrees = []
    for sentence in parsedText:
        if len(sentence.tokens) < 2:
            print("############################################")
            continue
        graph = sentence_to_graph(sentence)
        dependencyTrees.append(graph)
        governors = sorted(find_governors_from_graph(graph, None))
        tokenSpans = getSpans(graph, governors)
        words = [token.text for token in sentence.tokens]
        doc = Doc(nlp.vocab, words=words)
        doc.spans["sc"] = []

        print(sentence)
        #print(f"GOVS {governors}")
        for span in tokenSpans:
            span = sorted(list(span))
            #print(f"SPAN {span}")
            for i, gov in enumerate(governors):
                if gov in span:
                    idx = i
                    break
            if check_continuity(span):
                span = [nodeID for nodeID in span if graph.nodes[nodeID]['token'].deprel not in {"mark", "cc"} and graph.nodes[nodeID]['token'].text not in PUNCT]
                doc.spans["sc"].append(Span(doc, min(span)-1, max(span), f"{idx+1}. człon"))
            else:
                span = removeSingleTokens(span)
                if check_continuity(span):
                    span = [nodeID for nodeID in span if graph.nodes[nodeID]['token'].deprel  not in {"mark", "cc"} and graph.nodes[nodeID]['token'].text not in PUNCT]
                    doc.spans["sc"].append(Span(doc, min(span)-1, max(span), f"{idx+1}. człon"))
                else:
                    span = [nodeID for nodeID in span if graph.nodes[nodeID]['token'].deprel  not in {"mark", "cc"}  and graph.nodes[nodeID]['token'].text not in PUNCT]
                    splits = findSplit(span)
                    if splits != []:
                        for split in splits:
                            doc.spans["sc"].append(Span(doc, min(span)-1, split[0], f"{idx+1}. człon"))
                            doc.spans["sc"].append(Span(doc, split[1]-1, max(span), f"{idx+1}. człon"))
                    else:
                        doc.spans["sc"].append(Span(doc, min(span)-1, max(span), f"{idx+1}. człon"))
        docs.append(doc)
    return docs

def segmentFile(text, model, nlp):
    parsedText = model(text)
    docs = prepareDoc(parsedText, nlp)
    
    options = {"colors": {key: value for key, value 
                    in zip([f"{i+1}. człon" for i in range(MAX_UNITS)], COLORS_NAMES)}}
    html = spacy.displacy.render(docs, style="span", options=options)  # or style="ent" for NER
    return html

def getFile(filePath):
    with open("data/TypeSystem.xml", "rb") as f:
        typesystem = cassis.load_typesystem(f)

    with open(filePath, "rb") as g:#"data/XMI_train/train/206.xmi"
        cas = cassis.load_cas_from_xmi(g, typesystem)
    
    return cas
def main(folder):
    nlp_blank = spacy.blank("pl")
    combo = COMBO.from_pretrained("polish-herbert-base-ud213")
    dir = os.fsencode(folder)
    #with open("tekst.txt", "r", encoding="utf-8") as f:
     #      text = f.read()
   # with open("out.html", "w", encoding="utf-8") as f:
     #       f.write(segmentFile(html.unescape(text), combo, nlp_blank))

    for file in os.listdir(dir):
        #if file == b'159.xmi':
        print(os.path.splitext(file)[0].decode())
        cas = getFile(os.path.join(dir, file))        
        with open(f"segmented/{os.path.splitext(file)[0].decode()}.html", "w", encoding="utf-8") as f:
            f.write(segmentFile(prepareString(html.unescape(cas.sofa_string)), combo, nlp_blank))
           
if __name__== "__main__":
    main("data/XMI_dev/dev")
