import spacy
import ads
import sys
from combo.predict import COMBO
from spacy import displacy
from spacy.tokens import Doc
from spacy.tokens import Span



MAX_UNITS = 60
COLORS_NAMES = 60*["navajowhite"]
'''["turquoise", " lightcoral", "mediumorchid", 
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
                "crimson", "olive", "k", "plum", "wheat", "royalblue"]'''
# Download Polish model. Change cuda value to use GPU
def get_words(tokens):
    words = []
    for token in tokens:
        if token.deprel[0:3] != "aux":
            words.append(token.text)
        else:
            words[-1] += token.text
    return words

def prepare_multiple_sentences(text, nlp_blank):
    docs = []

    '''for sentence in text:
        tokens = sentence.tokens
        words = [token.text for token in tokens]
        spans = ads.remove_punct(tokens, ads.find_spans(tokens))
        doc = Doc(nlp_blank.vocab, words=words)
        doc.spans["sc"] = [Span(doc, min(span), max(span)+1, f"{i+1}. człon") for i, span in enumerate(spans)]
        docs.append(doc)
        allSpans.append(spans)'''
    tokens=[]
    tokenOffset = 0
    for sentence in text:
        for token in sentence.tokens:
            token.idx += tokenOffset
            token.head += tokenOffset
        tokens += sentence.tokens
        tokenOffset += len(sentence.tokens)

    words = [token.text for token in tokens]
    spans = ads.remove_punct(tokens, ads.find_spans(tokens))
    #print(spans)
    doc = Doc(nlp_blank.vocab, words=words)
    doc.spans["sc"] = [Span(doc, min(span), max(span)+1, f"{i+1}. człon") for i, span in enumerate(spans) if span != []]
    return doc 

def run_segmentation(text, model, nlp):
    options = {"colors": {key: value for key, value 
                    in zip([f"{i+1}. człon" for i in range(MAX_UNITS)], COLORS_NAMES)}}
    
    prediction = model(text)
    docs = prepare_multiple_sentences(prediction, nlp)
    if len(docs) == 1:
        docs = docs[0]
    return docs, options

def get_text(file):
    with open(file, "r", encoding='utf-8') as f:
        text = f.read()
    return text

def main(text, model, nlp):
    docs, options = run_segmentation(text, model, nlp)
    #displacy.serve(docs, style="span", options=options)
    return docs, options

if __name__ == "__main__":
    main(get_text(sys.argv[1]))
