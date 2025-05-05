import spacy
import ads
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
    for sentence in text:
        tokens = sentence.tokens
        words = [token.text for token in tokens]
        spans = ads.remove_punct(tokens, ads.find_spans(tokens))
        #print(f"SPAN: {spans}")
        doc = Doc(nlp_blank.vocab, words=words)
        doc.spans["sc"] = [Span(doc, min(span), max(span)+1, f"{i+1}. człon") for i, span in enumerate(spans)]
        docs.append(doc)
    return docs

def run_segmentation(text):
    combo = COMBO.from_pretrained("english-bert-base-ud213")
    nlp_blank = spacy.blank("pl")

    #text = (f"Deszcz padał, więc wróciłem do domu i postanowiłem zjeść placki. Wieczorem obejrzałem super film i poszedłem spać na komputerze. Lubię zbierać grzyby."
    #        f"Deszcz padał, więc wróciłem do domu, a potem zjadłem placki. Wieczorem obejrzałem super film i poszedłem spać na komputerze. Lubię zbierać grzyby, a czasami także klocki lego.")
    prediction = combo(text)

    options = {"colors": {key: value for key, value 
                    in zip([f"{i+1}. człon" for i in range(MAX_UNITS)], COLORS_NAMES)}}

    docs = prepare_multiple_sentences(prediction, nlp_blank)
    if len(docs) == 1:
        docs = docs[0]
    return docs, options

#docs, options = run_segmentation('SSs')

#displacy.serve(docs, style="span", options=options)
