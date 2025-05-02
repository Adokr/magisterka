import streamlit as st
import spacy
from spacy_streamlit import visualize_spans
from combo.predict import COMBO
import demo

st.text_input("Enter a sentence for segmentation", key="sentence")
docs, options = demo.run_segmentation(st.session_state.sentence)

visualize_spans(docs, spans_key="sc", displacy_options=options)