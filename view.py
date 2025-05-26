import cassis
import demo
import os
import spacy
from combo.predict import COMBO
from spacy import displacy
from spacy.tokens import Doc, SpanGroup, Span


def compare(predictedSpans, trueSpans):
    countSameSpans = 0
    spansCountDiff = len(predictedSpans) - len(trueSpans)

    textTrueSpans = [item.orth_ for item in trueSpans]
    for span in predictedSpans:
        if span.orth_ in textTrueSpans:
            countSameSpans += 1

    return countSameSpans, spansCountDiff, len(trueSpans) == countSameSpans

def getFile(filePath):
    with open("data/TypeSystem.xml", "rb") as f:
        typesystem = cassis.load_typesystem(f)

    with open(filePath, "rb") as g:#"data/XMI_train/train/206.xmi"
        cas = cassis.load_cas_from_xmi(g, typesystem)
    
    return cas

def getTrueSpans(casFile):
    nlp_blank = spacy.blank("pl")
    words = [word for word in casFile.sofa_string.split(" ")]
    doc = Doc(nlp_blank.vocab, words=words)
    #start = casFile.select("DocumentMetaData")[0].get("begin")
    end = casFile.select("DocumentMetaData")[0].get("end")
    trueSpans = []
    trueSpansInChars = []

    for discourseSpan in casFile.select("DiscourseSpans"):
        span = [discourseSpan.get("begin"), discourseSpan.get("end")]
        if discourseSpan.get("end") <= end and span not in trueSpansInChars:
            trueSpansInChars.append(span)
    
    for i, span in enumerate(trueSpansInChars):
        #print(f"start: {span[0]}")
        #print(f"end: {span[1]}")
        trueSpans.append(doc.char_span(span[0], span[1], f"{i+1}. człon"))
    
    doc.spans["sc"] = SpanGroup(doc, name="sc", spans=trueSpans)

    return doc

def removeSomeSpaces(text):
    formattedText = ""
    spaceNext = False
    for string in text.split():
        if string not in {",", ".", "(", ")", "!", "?", ":", ";"}:
            if spaceNext:
                formattedText += " "
            formattedText += string
            spaceNext = True
        elif string not in {"(", ")"}:
            formattedText += string
            spaceNext = True
        elif string == "(":
            formattedText += " " + string
            spaceNext = False
        else:
            formattedText = formattedText.rstrip(" ") + string
            spaceNext = True
    return formattedText

def main(folder):
    combo = COMBO.from_pretrained("polish-herbert-base-ud213")
    nlp_blank = spacy.blank("pl")
    trueSpansCount = 0
    goodPredictionCount = 0
    wholeFilePredictedCount = 0
    tooManySpans = 0
    tooFewSpans = 0
    fileCount = 0
    dir = os.fsencode(folder)
    for file in os.listdir(dir):
        if file == b"159.xmi":
            print(file)
            fileCount += 1
            cas = getFile(os.path.join(dir, file))
            trueDocs = getTrueSpans(cas)
            predictedDocs, options, predictedSpan = demo.main(removeSomeSpaces(cas.sofa_string), combo, nlp_blank)
            displacy.serve([predictedDocs, trueDocs], style="span", options=options)
            goodPredictions, diffCount, wholeFileGood = compare(predictedDocs.spans["sc"], trueDocs.spans["sc"])
            if wholeFileGood:
                wholeFilePredictedCount += 1
            elif diffCount < 0:
                tooFewSpans += 1
            elif diffCount > 0:
                tooManySpans += 1
            goodPredictionCount += goodPredictions
            trueSpansCount += len(trueDocs.spans["sc"])

            print( f"Well predicted spans: {goodPredictionCount}\t"
                    f"All spans: {trueSpansCount}\t"
                    f"%: {goodPredictionCount/trueSpansCount}\n\n")

        if fileCount == 100:
            break
    print(f"All file predicted well: {wholeFilePredictedCount}\t"
          f"File count: {fileCount}\t"
          f"%: {wholeFilePredictedCount/fileCount}\n\n"
          f"Well predicted spans: {goodPredictionCount}\t"
          f"All spans: {trueSpansCount}\t"
          f"%: {round(goodPredictionCount/trueSpansCount, 3)}\n\n"
          f"Too many: {tooManySpans}\t"
          f"Too few: {tooFewSpans}\n\n")

    #displacy.serve([predictedDocs, trueDocs], style="span", options=options)


if __name__ == "__main__":
    main("data/XMI_dev/dev")
    

