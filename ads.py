import networkx as nx
from combo.predict import COMBO
import spacy
from spacy.tokens import Doc, Span
import matplotlib.pyplot as plt
import os
import cassis
import html
import re
import string
import sys

TAGS = {'ccomp', 'csubj', 'parataxis:insert', 'parataxis:obj', 'acl:relcl', 'root'} # ccomp
VERB_TAGS = {'conj', 'acl:relcl', 'advcl', 'ccomp:obj', 'ccomp:cleft'}
PUNCT = {",", ".", ";", ":", "-", '"', "?", "!"}
ABBREVIATIONS = {"np.", "itd.", "itp.", "dr.", "prof.", "ul.", "al.", "sz.", "tzw.", "reż.", "godz.", "min.",
                 "str.", "cz.", "fot.", "art.", "lit.", "ust.", "in.",
                 *[f"{i}." for i in range(24)], *[f"{letter}." for letter in string.ascii_lowercase]}

ABBREVIATIONS_WITH_NAME_AFTER = {"dr.", "reż.", "ul.", "al."}

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
    new = cleaned_text
    '''new = ""
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
            skip = False'''
    
    finalText = []
    for i, word in enumerate(new.split()):
        if word.lower() not in ABBREVIATIONS:
            finalText.append(word)
        elif new.split()[i+1].islower() or new.split()[i+1].isnumeric() or word.lower() in ABBREVIATIONS_WITH_NAME_AFTER:
            finalText.append("".join(word)[:-1])
        else:
            print("LOL")
            print(word)
            finalText.append(word)
    print(f"TEXT: {' '.join(finalText)}")
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
        elif token.upostag == "ADJ" and token.deprel in VERB_TAGS and graph.nodes[root]['token'].upostag not in {"ADJ", "NOUN"}:
            governors.append(token.idx)
        elif token.upostag == "ADV" and token.deprel in {"advcl:relcl", "advcl"} and check_successors(graph, token, {"VERB"}, {"xcomp", "aux"}):
            governors.append(token.idx)
        elif token.upostag == "NOUN" and token.deprel == "advcl" and check_successors(graph, token, {"AUX"}, {"cop"}):
            governors.append(token.idx)
        governors.extend(find_governors_from_graph(graph, successor))
    return governors

def check_successors(graph, token, searchedUpostag, searchedDeprel):
    foundToken = False
    for successor in graph.successors(token.idx):
        if graph.nodes[successor]['token'].upostag in searchedUpostag and graph.nodes[successor]['token'].deprel in searchedDeprel:
            foundToken = graph.nodes[successor]
            break
    return foundToken


def sentence_to_graph(sentence):
    G = nx.DiGraph()
    for token in sentence.tokens:
        G.add_node(token.idx, token=token)   

    for token in sentence.tokens:
        if token.head != 0:
            G.add_edge(token.head, token.idx, label=token.deprel)
    print("\n################################################")
    for node in G.nodes:
        print(f"NODES: {node, G.nodes[node]['token'], G.nodes[node]['token'].deprel, G.nodes[node]['token'].head, G.nodes[node]['token'].upostag }")

    return G

def getSpans(graph, spanHeads):
    spans = []
    properSpans = []
    markers = []
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
    
    toRemove = []
    for span in spans:    
        for token in span:
            if graph.nodes[token]['token'].deprel == "mark":
                if token > 1 and graph.nodes[token-1]['token'].deprel == "punct":
                    markers.append([token-1, token])
                    toRemove.extend([token-1, token])
                else:
                    markers.append([token])
                    toRemove.append(token)
            elif graph.nodes[token]['token'].deprel == "cc":
                if not ((graph.nodes[token]['token'].head in span) and (graph.nodes[graph.nodes[token]['token'].head]['token'].head in span)):
                    if token > 1 and graph.nodes[token-1]['token'].deprel == "punct":
                        markers.append([token-1, token])
                        toRemove.extend([token-1, token])
                    else:
                        markers.append([token])
                        toRemove.append(token)
                
    for el in toRemove:
        for span in spans:
            if el in span:
                span.remove(el)

    #textSpans = []
    #for span in properSpans:
     #   textSpans.append(" ".join([graph.nodes[nodeID]['token'].text for nodeID in graph.nodes if nodeID in span]))
    return properSpans, markers

def check_continuity(my_list):
    return all(a+1==b for a, b in zip(my_list, my_list[1:]))

def removeSingleTokens(my_list, sentenceTokens):
    new_list = []
    if len(my_list) > 2:
        for i, el in enumerate(my_list):
            if sentenceTokens[i].upostag not in {"punct", "mark"} or not(el+1 not in my_list and el-1 not in my_list):
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

    whichSentences = [0, -1]
    if len(sys.argv) > 3:
        whichSentences = [int(sys.argv[3]), int(sys.argv[3])+1]
    print(whichSentences)
    
    for sentence in parsedText[whichSentences[0] : whichSentences[1]]:
        if len(sentence.tokens) < 2:
            print("############################################")
            continue
        graph = sentence_to_graph(sentence)
        dependencyTrees.append(graph)
        governors = find_governors_from_graph(graph, None) #if sorted then segmentes are numerated by the governors order
        tokenSpans, discourseMarkers = getSpans(graph, governors)
        words = [token.text for token in sentence.tokens]
        doc = Doc(nlp.vocab, words=words)
        doc.spans["sc"] = []

        print(sentence)
        print(f"GOVS {governors}")
        print(f"MARKER {discourseMarkers}")
        for markerGroup in discourseMarkers:
            doc.spans["sc"].append(Span(doc, min(markerGroup)-1, max(markerGroup), f"DM"))

        for preSpan in tokenSpans:
            preSpan = list(preSpan)
            span = []
            discourseMarkers = []
            punctuation = []
            
            #add period to the last segment
            if (len(graph)-1) in preSpan:
                if len(graph) not in preSpan:
                    preSpan.append(len(graph))
            elif len(graph) in preSpan:
                preSpan.remove(len(graph))

            if graph.nodes[1]['token'].upostag == "PUNCT":
                if 1 in preSpan and 2 not in preSpan:
                        preSpan.remove(1)
                        print("usun")
                if 1 not in preSpan and 2 in preSpan:
                    preSpan.append(1)
                    print("dodaj")
            
            preSpan = sorted(preSpan)
            print(f"SPAN {preSpan}")


            for i, gov in enumerate(governors):
                if gov in preSpan:
                    idx = i
                    break
            if check_continuity(preSpan):
                #for nodeID in preSpan:
                 #   if graph.nodes[nodeID]['token'] not in {'mark', 'cc'} and graph.nodes[nodeID]['token'].text not in PUNCT:
                  #      span.append(nodeID)
                   # elif graph.nodes[nodeID]['token'] in {'mark', 'cc'}:
                    #    discourseMarkers.append(nodeID)
                    #else:
                     #   punctuation.append(nodeID)

                span = [nodeID for nodeID in preSpan] #if graph.nodes[nodeID]['token'].deprel not in {"mark", "cc"}] #and graph.nodes[nodeID]['token'].text not in PUNCT]
                doc.spans["sc"].append(Span(doc, min(span)-1, max(span), f"{idx+1}. człon"))
            else:
                preSpan = removeSingleTokens(preSpan, sentence.tokens[:-1])#[:-1] żeby kropki nie brać
                print(f"afterremove: {preSpan}")
                if check_continuity(preSpan):
                    print(f"cont")
                    preSpan = [nodeID for nodeID in preSpan if graph.nodes[nodeID]['token'].deprel  not in {"mark", "cc"}]# and graph.nodes[nodeID]['token'].text not in PUNCT]
                    print(preSpan)
                    doc.spans["sc"].append(Span(doc, min(preSpan)-1, max(preSpan), f"{idx+1}. człon"))
                else:
                    print(f"not cont")
                    preSpan = [nodeID for nodeID in preSpan if graph.nodes[nodeID]['token'].deprel not in {"mark"}]#  and graph.nodes[nodeID]['token'].text not in PUNCT]
                    splits = findSplit(preSpan)
                    print(preSpan, splits)
                    if splits != []:
                        for i in range(len(splits)):
                            if i == 0:
                                doc.spans["sc"].append(Span(doc, min(preSpan)-1, splits[i][0], f"{idx+1}. człon"))
                                if len(splits) == 1:
                                    doc.spans["sc"].append(Span(doc, splits[i][1]-1, max(preSpan), f"{idx+1}. człon"))
                            elif i < len(splits)-1:
                                doc.spans["sc"].append(Span(doc, splits[i-1][1]-1, splits[i][0], f"{idx+1}. człon"))
                            else:
                                doc.spans["sc"].append(Span(doc, splits[i-1][1]-1, splits[i][0], f"{idx+1}. człon"))
                                doc.spans["sc"].append(Span(doc, splits[i][1]-1, max(preSpan), f"{idx+1}. człon"))
                    else:
                        doc.spans["sc"].append(Span(doc, min(preSpan)-1, max(preSpan), f"{idx+1}. człon"))
        docs.append(doc)
    return docs

def segmentFile(text, model, nlp):
    parsedText = model(text)
    docs = prepareDoc(parsedText, nlp)
    
    options = {"colors": {key: value for key, value 
                    in zip([f"{i+1}. człon" for i in range(MAX_UNITS)], COLORS_NAMES)}}
    options["colors"]["DM"] = "red"
    html = spacy.displacy.render(docs, style="span", options=options)  # or style="ent" for NER
    return html

def getFile(filePath, folder):
    with open(os.path.join(folder, "TypeSystem.xml"), "rb") as f:
        typesystem = cassis.load_typesystem(f)

    with open(filePath, "rb") as g:#"data/XMI_train/train/206.xmi"
        cas = cassis.load_cas_from_xmi(g, typesystem)
    
    return cas
def main(folder):
    nlp_blank = spacy.blank("pl")
    combo = COMBO.from_pretrained("polish-herbert-base-ud213")
    dir = os.fsencode(os.path.join(folder, "XMI_dev/dev"))
   
    onlyOneFile = False
    if len(sys.argv) > 2:
        onlyOneFile = True

    print(os.getcwd())
    outputDir = "../segmented/"
    if not os.path.isdir(outputDir):
        os.mkdir(outputDir)

    if onlyOneFile:
        file = os.fsencode(sys.argv[2])
        cas = getFile(os.path.join(dir, file), folder)        
        with open(f"{os.path.join(outputDir, os.path.splitext(file)[0].decode())}.html", "w", encoding="utf-8") as f:
            f.write(segmentFile(prepareString(html.unescape(cas.sofa_string)), combo, nlp_blank))
    else:
        for file in os.listdir(dir):
            #if file == b'46.xmi':
            print(os.path.splitext(file)[0].decode())
            cas = getFile(os.path.join(dir, file), folder)        
            with open(f"{os.path.join(outputDir, os.path.splitext(file)[0].decode())}.html", "w", encoding="utf-8") as f:
                f.write(segmentFile(prepareString(html.unescape(cas.sofa_string)), combo, nlp_blank))

if __name__== "__main__":
    main(sys.argv[1])   #"../data/XMI_dev/dev")
