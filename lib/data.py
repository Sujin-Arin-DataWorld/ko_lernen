"""Datenlader mit Streamlit-Cache — wird einmal pro App-Session geladen."""
from pathlib import Path
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent.parent / "data"


@st.cache_data(show_spinner=False)
def load_vocab() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "korean_vocab.csv")


@st.cache_data(show_spinner=False)
def load_grammar() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "grammar.csv")


@st.cache_data(show_spinner=False)
def load_listening_sentences() -> pd.DataFrame:
    df_vocab = load_vocab()
    df_grammar = load_grammar()
    rows = []
    for _, r in df_vocab.iterrows():
        if pd.notna(r.example_korean) and len(str(r.example_korean)) > 3:
            rows.append({
                "korean":  r.example_korean,
                "german":  r.example_german,
                "roman":   "",
                "level":   r.level,
                "topic":   r.topic,
                "source":  "Vokabel",
                "keyword": r.korean,
            })
    for _, r in df_grammar.iterrows():
        if pd.notna(r.example_korean) and len(str(r.example_korean)) > 3:
            rows.append({
                "korean":  r.example_korean,
                "german":  r.example_german,
                "roman":   "",
                "level":   r.level,
                "topic":   r.type_de,
                "source":  "Grammatik",
                "keyword": r.pattern,
            })
    return pd.DataFrame(rows).drop_duplicates(subset=["korean"]).reset_index(drop=True)
