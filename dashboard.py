import streamlit as st
import spacy
from spacy_streamlit import visualize_spans
from combo.predict import COMBO
import demo


if __name__ == "__main__":
    combo = COMBO.from_pretrained("polish-herbert-base-ud213")
    nlp_blank = spacy.blank("pl")

    st.title("Automatic Discourse Segmentation")

    if "text_history" not in st.session_state:
        st.session_state.text_history = []

    user_input = st.text_area("Enter a sentence to segment", key="text_input", height=100)

    if st.button("Segment text"):
        if user_input.strip():
            docs, options = demo.run_segmentation(user_input, combo, nlp_blank)
            st.session_state.text_history.extend(docs)
            #st.session_state.text_input = ""
            print("user_input")

    print("before vis")
    for doc in st.session_state.text_history:
        print("in vis")
        visualize_spans(doc, spans_key="sc", displacy_options=options)
        print("after vis")
            #st.text_input("Enter another sentence for segmentation", key="sentence1")

            #docs, options = demo.run_segmentation(st.session_state.sentence1)

            #visualize_spans(docs, spans_key="sc", displacy_options=options)
