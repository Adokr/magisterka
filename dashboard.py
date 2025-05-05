import streamlit as st
import spacy
from spacy_streamlit import visualize_spans
from combo.predict import COMBO
import demo


if __name__ == "__main__":
    combo = COMBO.from_pretrained("polish-herbert-base-ud213")
    nlp_blank = spacy.blank("pl")

    st.title("Automatic Discourse Segmentation")
    user_input = st.text_area("Enter a sentence to segment", height=150)

    if user_input.strip():
        docs, options = demo.run_segmentation(user_input, combo, nlp_blank)

        visualize_spans(docs, spans_key="sc", displacy_options=options)

        #st.text_input("Enter another sentence for segmentation", key="sentence1")

        #docs, options = demo.run_segmentation(st.session_state.sentence1)

        #visualize_spans(docs, spans_key="sc", displacy_options=options)
