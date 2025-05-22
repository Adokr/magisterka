import spacy
import ads
import sys
from combo.predict import COMBO
from spacy import displacy
from spacy.tokens import Doc
from spacy.tokens import Span



MAX_UNITS = 7
COLORS_NAMES = ["turquoise", " lightcoral", "mediumorchid", 
                "sandybrown", "palegreen", "deepskyblue",
                "hotpink"]
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
    allSpans = []
    for sentence in text:
        tokens = sentence.tokens
        words = [token.text for token in tokens]
        spans = ads.remove_punct(tokens, ads.find_spans(tokens))
        doc = Doc(nlp_blank.vocab, words=words)
        doc.spans["sc"] = [Span(doc, min(span), max(span)+1, f"{i+1}. człon") for i, span in enumerate(spans)]
        docs.append(doc)
        allSpans.append(spans)
    return docs, allSpans

def run_segmentation(text, model, nlp):
    options = {"colors": {key: value for key, value 
                    in zip([f"{i+1}. człon" for i in range(MAX_UNITS)], COLORS_NAMES)}}
    
    prediction = model(text)
    docs, spans = prepare_multiple_sentences(prediction, nlp)
    if len(docs) == 1:
        docs = docs[0]
    return docs, options, spans

def get_text(file):
    with open(file, "r", encoding='utf-8') as f:
        text = f.read()
    return text

def main(text):
    combo = COMBO.from_pretrained("polish-herbert-base-ud213")
    nlp_blank = spacy.blank("pl")
    docs, options, spans = run_segmentation(text, combo, nlp_blank)
    #displacy.serve(docs, style="span", options=options)
    return docs, options, spans

if __name__ == "__main__":
    main(get_text(sys.argv[1]))
