import ads_en
import sys
import csv
import re
from combo.predict import COMBO
import spacy
import conll_to_dg as dg
import os
import pathlib 
PATH ="C:\\Users\\Adam\\magisterka\\data"


def getData():
    text_tab = []
    tokenized_text = []
    du_beginnings = []
    sent_ids = []
    badly_segmented = {"GUM_bio_byron-25", "GUM_conversation_grounded-16", 
                       "GUM_conversation_grounded-84", "GUM_conversation_grounded-115", "GUM_court_loan-8",
                       "GUM_court_loan-31",  "GUM_essay_evolved-31", "GUM_essay_evolved-58",
                       "GUM_fiction_beast-10", "GUM_interview_cyclone-4", "GUM_interview_cyclone-18", "GUM_interview_cyclone-24",
                       "GUM_letter_arendt-12", "GUM_letter_arendt-19", "GUM_news_iodine-36",
                       "GUM_podcast_wrestling-58", "GUM_podcast_wrestling-71", "GUM_speech_impeachment-10", "GUM_speech_inauguration-5",
                       "GUM_speech_inauguration-20", "GUM_vlog_portland-35", "GUM_vlog_portland-51", "GUM_vlog_portland-53"
                       } 
    
    with open(r'C:\\Users\Adam\\magisterka\\data\\ENG\\eng.erst.gum_dev.conllu', "r", encoding="utf8") as data_file:
        reader = csv.reader(data_file, delimiter="\t")
        
        
        
        for row in reader:
            #print(row)
            if row != []:
                ugh = row[0].split(" ")
                if len(ugh) > 3:
                    if ugh[0:2] == ["#",  "text"] and sent_ids[-1] not in badly_segmented:
                        text_tab.append(ugh[3:])
                    elif ugh[0:3] == ["#", "newdoc", "id"]:
                        text_tab.append(ugh) #newdoc id
                    elif ugh[0:2] == ["#", "sent_id"]:
                        sent_ids.append(ugh[3])

    with open(r'C:\\Users\Adam\\magisterka\\data\\ENG\\eng.erst.gum_dev.conllu', "r", encoding="utf8") as data_file:
        reader1 = csv.reader(data_file, delimiter="\t")
        tokenized_sentence = []
        discourse_unit_beginning = []
        for row in reader1:
            #print(row)
            if row != []:
                #print(row)
                if row[0].isnumeric() and row[0] != "#":
                    tokenized_sentence.append(row[1])
                    if re.search(r"Seg=B-seg", row[-1]):
                        discourse_unit_beginning.append(row[0])
                    #print(row[1])
                else:
                    #print(sentence)
                    if tokenized_sentence != []:
                        tokenized_text.append(tokenized_sentence)
                    if discourse_unit_beginning != []:
                        du_beginnings.append(discourse_unit_beginning)
                    discourse_unit_beginning = []
                    tokenized_sentence = []
    text = [" ".join(sentence) for sentence in text_tab]

    return text, text_tab, tokenized_text, du_beginnings, sent_ids

def getGraphFromConllu():
    try:
        conllu = open('C:\\Users\\Adam\\magisterka\\data\\ENG\\eng.erst.gum_dev.conllu', 'r', encoding="utf8")
    except IOError:
        print("The input conllu file not found")
        sys.exit(1)
    except IndexError:
        print("python", sys.argv[0], "inputfile outputfile")
        sys.exit(1)
    
    digraphs = dg.read_graph(conllu, 2)
    return digraphs

def prepareData(discourse_unit_start, text):
    #print(f"DU {discourse_unit_start}")
    #print(f"TOKENS: {text}")
    
    beginnings = []

    tmp = []
    for item in zip(text, discourse_unit_start):
        #print(f"ITEM {item}")
        if item[0][0]!="#":
            tmp = ["Seg=O"] * len(item[0][0].tokens)
            
            
            print(f"tokens len: {len(item[0][0].tokens), item[0][0]}")
            #print(f"disc len: {len(item[1]), item[1]}")

            for el in item[1]:
                #print(f"EL {el}")
                tmp[el-1] = "Seg=B-seg"
            beginnings.append(tmp)
        else:
            beginnings.append([None])
    return beginnings

def main():
    graphs = getGraphFromConllu()
    text, text_tab, tokenized_text, du_beginnings, sent_ids = getData()

    predicted_beginnings = []
    predicted_tokenization = []
    tokenization_proper =[]
    #print(text[76:77])
    for i, graph in enumerate(graphs):
        
        beginnings, tokenization = ads_en.prepareDoc(graph)
        predicted_tokenization.append(tokenization)
        predicted_beginnings.append(beginnings)
    
    #print(predicted_tokenization)
    beginning_proper = prepareData(predicted_beginnings, predicted_tokenization)
    for item in predicted_tokenization:
        if isinstance(item, list):
            tokenization_proper.append(item[0].tokens)
        else:
            tokenization_proper.append(item)
    #tokenization_proper = [item[0].tokens for item in predicted_tokenization if isinstance(item, list) else item]
    #print(tokenization_proper)


    with open(r'C:\\Users\Adam\\magisterka\\data\\ENG\\predicted.tok', "w", encoding="utf8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        i = 1
        for item in zip(tokenization_proper, beginning_proper):
            #print(f"ITEM {item}")
            if item[1] != [None]:
                for j in range(len(item[0])):
                    row = [i, item[0][j], "_", "_", "_", "_", "_", "_", "_", item[1][j]]
                    writer.writerow(row)
                    i += 1
            else:
                if i != 1:
                    writer.writerow("")
                writer.writerow([item[0]])
                i = 1


if __name__ == "__main__":
    main()
