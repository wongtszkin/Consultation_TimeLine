# -*- coding: utf-8 -*-
"""Untitled16.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EnrNCH7HkrJRr4cCa1O0AM4eOn1lIVSW
"""
import streamlit as st
import matplotlib.pyplot as plt
from datetime import date
from datetime import datetime
import numpy as np
import spacy
import re

from typing import List, Sequence, Tuple, Optional

import pandas as pd
import streamlit as st
import spacy
from spacy import displacy

NER_ATTRS = ["text", "label_", "start", "end", "start_char", "end_char"]

def get_html(html: str):
    """Convert HTML so it can be rendered."""
    WRAPPER = """<div style="overflow-x: auto; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem; margin-bottom: 2.5rem">{}</div>"""
    # Newlines seem to mess with the rendering
    html = html.replace("\n", "")
    return WRAPPER.format(html)

def visualize_ner(
    doc: spacy.tokens.Doc,
    *,
    labels: Sequence[str] = tuple(),
    attrs: List[str] = NER_ATTRS,
    show_table: bool = True,
    title: Optional[str] = "Analysis List",
    sidebar_title: Optional[str] = "Named Entities",
    key=None,  # add key as parameter
) -> None:
    """Visualizer for named entities."""
    if title:
        st.header(title)
    if sidebar_title:
        st.sidebar.header(sidebar_title)
    label_select = st.sidebar.multiselect(
        "Entity labels", options=labels, default=list(labels), key=key # add key now
    )
    html = displacy.render(doc, style="ent", options={"ents": label_select})
    style = "<style>mark.entity { display: inline-block }</style>"
    st.write(f"{style}{get_html(html)}", unsafe_allow_html=True)
    if show_table:
        data = [
            [str(getattr(ent, attr)) for attr in attrs]
            for ent in doc.ents
            if ent.label_ in labels
        ]
        df = pd.DataFrame(data, columns=attrs)
        st.dataframe(df)
        
st.title('Consultation TimeLine Converter')
txt = st.text_area('Input your consultation notes:', "")



#####
if st.button('Spacy'):
    st.title('Converted Result:')
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(txt)

    date_save = []
    date_start = []
    date_end = []

    event_save = []
    event_start = []
    event_end = []

    Noun_List = []

    # Check Date by NLP
    for ent in filter(lambda e: e.label_=='DATE' ,doc.ents):
        print(ent.text, ent.label_, ent.start_char, ent.end_char)
        date_save.append(ent.text)
        date_start.append(ent.start_char)
        date_end.append(ent.end_char)

    # Check Event by NLP
    for ent in filter(lambda e: e.label_=='PERSON',doc.ents):
        print(ent.text, ent.start_char, ent.end_char)
        event_save.append(ent.text)
        event_start.append(ent.start_char)
        event_end.append(ent.end_char)

    # Check Date by formula
    for i in range(len(doc)):
        if doc[i].shape_ == 'd/dd/dd' or doc[i].shape_ =='dd/dd/dd':
           if (doc[i].text not in date_save):
              date_save.append(doc[i].text)
              date_start.append(doc[i].idx)
              date_end.append(len(doc[i].text)+doc[i].idx)
    
    from datetime import date
    dates = []
    labels = []

    event_save.append('progressive memory and cognitive decline')

    for i in range(len(date_save)):
        date_time_str = date_save[i]+' 00:00:00'
        date_time_obj = datetime.strptime(date_time_str, '%d/%m/%y %H:%M:%S')
        time = date_time_obj.strftime("%H:%M:%S")
        year = date_time_obj.strftime("%Y")
        month = date_time_obj.strftime("%m")
        day = date_time_obj.strftime("%d")
        year = int(year)
        month = int(month)
        day = int(day)
        dates.append(date(year,month,day))

    min_date = date(np.min(dates).year - 2, np.min(dates).month, np.min(dates).day)
    max_date = date(np.max(dates).year + 2, np.max(dates).month, np.max(dates).day)
     
    for i in range(len(event_save)):
        labels.append(event_save[i])
    # labels with associated dates
    labels = ['{0:%d %b %Y}:\n{1}'.format(d, l) for l, d in zip (labels, dates)]
    
    fig, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)
    _ = ax.set_ylim(-2, 1.75)
    _ = ax.set_xlim(min_date, max_date)
    _ = ax.axhline(0, xmin=0.05, xmax=0.95, c='deeppink', zorder=1)
     
    _ = ax.scatter(dates, np.zeros(len(dates)), s=120, c='palevioletred', zorder=2)
    _ = ax.scatter(dates, np.zeros(len(dates)), s=30, c='darkmagenta', zorder=3)
    label_offsets = np.zeros(len(dates))
    label_offsets[::2] = 0.35
    label_offsets[1::2] = -0.7
    for i, (l, d) in enumerate(zip(labels, dates)):
        _ = ax.text(d, label_offsets[i], l, ha='center', fontfamily='serif', fontweight='bold', color='royalblue',fontsize=12)
    stems = np.zeros(len(dates))
    stems[::2] = 0.3
    stems[1::2] = -0.3
    markerline, stemline, baseline = ax.stem(dates, stems, use_line_collection=True)
    _ = plt.setp(markerline, marker=',', color='darkmagenta')
    _ = plt.setp(stemline, color='darkmagenta')

    for spine in ["left", "top", "right", "bottom"]:
        _ = ax.spines[spine].set_visible(False)
     
    # hide tick labels
    _ = ax.set_xticks([])
    _ = ax.set_yticks([])
     
    _ = ax.set_title('Patient Event Timeline', fontweight="bold", fontfamily='serif', fontsize=16,
                     color='royalblue')
    st.pyplot(fig)
    visualize_ner(doc, labels=nlp.get_pipe("ner").labels, key=1)
    
    import json
    List_Dict = []

    for i in range(len(date_save)):
        
        date_time_str = date_save[i]+' 00:00:00'
        date_time_obj = datetime.strptime(date_time_str, '%d/%m/%y %H:%M:%S')
        date = date_time_obj.strftime("%d/%m/%Y")
        time = date_time_obj.strftime("%H:%M:%S")
        year = date_time_obj.strftime("%Y")
        month = date_time_obj.strftime("%m")
        day = date_time_obj.strftime("%d")
        
        addDict = {'Event':event_save[i],'Date': date, 'Year': year, 'Month':month, 'Day':day ,'Time':time ,'Start_pos':date_start[i], 'End_pos':date_end[i]}
        print(addDict)
        List_Dict.append(addDict)

    jsonString = json.dumps(List_Dict)
    jsonFile = open("data.json", "w")
    jsonFile.write(jsonString)
    jsonFile.close()
    st.title('Json Result of the Event:')
    st.json(jsonString)

#####



