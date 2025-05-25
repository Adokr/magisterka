import cassis
import demo
import spacy
from spacy import displacy
from spacy.tokens import Doc, SpanGroup, Span


def charSpanToTokenSpan(charSpans, doc):
    return None

if __name__ == "__main__":
    with open("data/TypeSystem.xml", "rb") as f:
        typesystem = cassis.load_typesystem(f)

    with open("data/XMI_train/train/206.xmi", "rb") as g:
        cas = cassis.load_cas_from_xmi(g, typesystem)

    print(f"###############\n{cas.sofa_string}\n##########")
    start = cas.select("DocumentMetaData")[0].get("begin")
    end = cas.select("DocumentMetaData")[0].get("end")

    #annotatedSpans = []
    thisSentenceSpans = []

    for discourseSpan in cas.select("DiscourseSpans"):
        span = [discourseSpan.get("begin"), discourseSpan.get("end")]
        if discourseSpan.get("end") <= end and span not in thisSentenceSpans:
            thisSentenceSpans.append(span)
    #annotatedSpans.append(thisSentenceSpans)
    print(f"SPANS: {thisSentenceSpans}")
    
    nlp_blank = spacy.blank("pl")
    
    words = [word for word in cas.sofa_string.split(" ")]
    #print(words)
    doc = Doc(nlp_blank.vocab, words=words)

    spans = []
    
    for i, span in enumerate(thisSentenceSpans):
        #print(f"start: {span[0]}")
        #print(f"end: {span[1]}")
        spans.append(doc.char_span(span[0], span[1], f"{i+1}. człon"))
    doc.spans["sc"] = SpanGroup(doc, name="sc", spans=spans)

    #print(f"DOCS: {lol}")
    docs, options, predictedSpan = demo.main(cas.sofa_string)
    
    #displacy.serve(docs, style="span", options=options)
    displacy.serve([docs, doc], style="span", options=options)
    print(predictedSpan)
