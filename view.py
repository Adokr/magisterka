import cassis
import demo
from spacy import displacy
from spacy.tokens import Doc
from spacy.tokens import Span


if __name__ == "__main__":
    with open("data/TypeSystem.xml", "rb") as f:
        typesystem = cassis.load_typesystem(f)

    with open("data/XMI_dev/dev/58.xmi", "rb") as g:
        cas = cassis.load_cas_from_xmi(g, typesystem)

    annotatedSpans = []
    thisSentenceSpans = []
    for discourseSpan in cas.select("DiscourseSpans"):
        thisSentenceSpans.append([discourseSpan.get("begin"), discourseSpan.get("end")])
    annotatedSpans.append(thisSentenceSpans)
    
    docs, options, predictedSpan = demo.main(cas.sofa_string)
    newDocs = []
    for i in range(len(docs)):
        newDocs.append(docs)
        newDocs.append()
    displacy.serve(docs, style="span", options=options)
    print(predictedSpan)
