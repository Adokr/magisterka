import streamlit as st
from spacy_streamlit import visualize_spans
import demo


if __name__ == "__main__":
    st.text_input("Enter a sentence for segmentation", key="sentence")
    docs, options = demo.run_segmentation(st.session_state.sentence)

    visualize_spans(docs, spans_key="sc", displacy_options=options)

    st.text_input("Enter another sentence for segmentation", key="sentence1")

    docs, options = demo.run_segmentation(st.session_state.sentence1)

    visualize_spans(docs, spans_key="sc", displacy_options=options)
