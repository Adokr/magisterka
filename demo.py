import spacy
#import ads
from combo.predict import COMBO
from spacy import displacy
from spacy.tokens import Doc

# Download Polish model. Change cuda value to use GPU
combo = COMBO.from_pretrained("polish-herbert-base-ud213")
nlp_blank = spacy.blank("pl")

sentence = "Deszcz padał, więc wróciłem do domu."
predicted = combo(sentence)[0].tokens


words = [item.text for item in predicted]
heads = [item.head - 1 if item.head > 0 else item.idx - 1 for item in predicted]
deps = [item.deprel for item in predicted]

for i, token in enumerate(predicted):
    token.head = heads[i]
    token.deps = deps[i]

doc = Doc(nlp_blank.vocab, words=words, heads=heads, deps=deps)

displacy.serve(doc, style="dep")
