
import codecs
import nltk
import string
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize 
from nltk.corpus import stopwords
import os, sys, re

try: reduce
except: from functools import reduce
try:    raw_input
except: raw_input = input

import PySimpleGUI as sg
sg.theme('DarkAmber')

PATH="C:/Users/a1098/Desktop/E16058_Karounis-ANTONIOS"
indexName="example-inverted-index.txt"

class Engine:

    def process_term(term): #removing punctuation from term. Lemmetizing and lowering the term (decided to not stem the terms since it negatively effected the results the engine was returing)

        lemmatizer = WordNetLemmatizer()
        #ps = PorterStemmer()
        translate_table = dict((ord(char), None) for char in string.punctuation)

        return (lemmatizer.lemmatize(term).lower()).translate(translate_table) 

    def load_data(path):  #function that reads data from given path and tokenizes their texts. Returns a set that contains all the words and a set that indexes the words based on the text file they originate from.
        
        texts, words = {}, set()                  
        
        try:
            for dirpath, dirnames, files in os.walk(path):
                for file_name in files:                                                                      
                    
                    file_full_name=os.path.join(dirpath, file_name)
    
                    f = codecs.open(file_full_name, "r", encoding="utf8", errors='ignore')                                                        

                    print("Loading data from "+file_full_name+"...")

                    terms = nltk.word_tokenize(f.read())                    

                    stop_words = set(stopwords.words("english"))
                    
                    tokens=[]

                    for term in terms:
                        
                        finishedWord = Engine.process_term(term)                        
                                                                        
                        if finishedWord not in stop_words and finishedWord!="":                                                                                                                                                     
                            tokens.append(finishedWord)                                                      
                            
                    words |= set(tokens)
                    texts[file_full_name.split('\\')[-1]] = tokens            
        
        except Exception as d:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("\n", exc_tb.tb_lineno,": There was an error loading the data: ", d,"\n")
            return        

        print("Data succesfully loaded")        
        return texts, words



    def saveInvIndex(filename, location, texts, words ): #saves the set that the load_data function outputs into a txt file in the given path
        
        save_path = location        
        completeName = os.path.join(save_path, filename)
        
        print("Saving index to "+completeName+"...")

        try:
            if os.path.exists(completeName): #removing the output file if it exists every time the function is called
                os.remove(completeName)
                    
            indexFile = open(completeName, "w")

            tenPercentLoader=len(words)*0.10
            counter,loader,percentage=0,0,0

            for word in words:
                line=str(word)+"\t"
                for txt, wrds in texts.items():
                    for wrdindx in (i for i,w in enumerate(wrds) if word==w):
                        if word in wrds:
                            line+="("+str(txt)+", "+str(wrdindx)+"), "
                line=line.strip(", ")
                line+="\n"            
                try:    
                    indexFile.write(line)
                    #print(line)    
                except:
                    pass    

                counter+=1
                if(counter>=loader+tenPercentLoader):
                    percentage+=10
                    print(str(percentage)+"%")
                    loader=counter            

        except IOError:
            print("The file is missing")

        print("Index succesfully saved")
        indexFile.close()


    def loadIndex(txtLocation): #loads index set from given txt file
        
        words, txts = {}, set()
        bad_chars = "()'',"        

        try:
            data = open(txtLocation)
            
            print("Loading index from "+txtLocation+"...")
            
            for line in data:
                toAdd=[]
                
                if "\t" in line:
                    dataSplit = line.split("\t")
                    word = dataSplit[0]    
                    
                insideParentheses = re.findall('\((.*?)\)',line)
                
                for term in insideParentheses:
                    txts.add(term.split(", ")[0])
                    wordData=(term.split(", ")[0], int(term.split(", ")[1]))
                    toAdd.append(wordData)

                words[word] = toAdd 

        except IOError as e:
            print("Error while loading file: "+str(e)+"\n")
        
        print("Index succesfully loaded")
        return words, txts

    def termsearch(terms, txts, finvindex): # Searches a inverted index for a set of terms
        
        somethings=set()
        tmpTerms=[]
        for term in terms:            
            tmpTerms.append(Engine.process_term(term)) 

        if not set(tmpTerms).issubset(set(finvindex.keys())):                        
            return set()
        
        return reduce(set.intersection,
                    (set(x[0] for x in txtindx)
                    for term, txtindx in finvindex.items()
                    if term in tmpTerms),
                    set(txts))
           
    
    def phrasesearch(phrase, txts, finvindex): # Searches a inverted index for a specific series of terms put together in a phrase

        wordsinphrase = phrase.strip().strip('"').split()

        for i, word in enumerate(wordsinphrase):           
            wordsinphrase[i] = Engine.process_term(wordsinphrase[i])
            
        
        if not set(wordsinphrase).issubset(set(finvindex.keys())):
            return set()

        firstword, otherwords = wordsinphrase[0], wordsinphrase[1:]
        found = []
        for txt in Engine.termsearch(wordsinphrase, txts, finvindex):
            # Possible text files
            for firstindx in (indx for t,indx in finvindex[firstword]
                            if t == txt):
                # Over all positions of the first word of the phrase in this txt
                if all( (txt, firstindx+1 + otherindx) in finvindex[otherword]
                        for otherindx, otherword in enumerate(otherwords) ):
                    found.append(txt)

        return found

while True:
    
    if(os.path.exists(PATH) == False): #Check if the PATH directory exists
        print("The PATH variable does not contain a directory that exists")
        break
    else:

        if(os.path.exists(os.path.dirname(os.path.realpath(__file__))+"/"+indexName)): #Check to see if the inverted index exists 

            #Load Index
            finvindex, txts = Engine.loadIndex(os.path.dirname(os.path.realpath(__file__))+"/"+indexName)

            #Create GUI 
            file_list_column = [
                [
                    sg.Text("Search for a specific term or phrase"),
                    sg.In(size=(45, 1), enable_events=True, key="-INPUT-"),
                    sg.Button(button_text="Search", enable_events=True, key="-SEARCH-")
                ],
                [
                    sg.Listbox(
                        values=[], enable_events=True, size=(40, 20), key="-TXT LIST-"
                    )
                ],
                
            ]

            button_column=[[sg.Button(button_text="How to use", enable_events=True, key="-HOWTOUSE-")]]

            layout = [[sg.Column(file_list_column)], [sg.VSeperator()], [sg.Column(button_column)]]

            # Create the window
            window = sg.Window("Text File Search Engine", layout)

            while True:
                event, values = window.read()

                if(event=="-SEARCH-"): #user begins a query

                    expressionStrings=[]
                    text=[]
                    results=set()

                    if(len(window['-INPUT-'].Get())>0):
                        text = window['-INPUT-'].Get()
                        expressionStrings=text.split(" OR ")            

                        for expression in expressionStrings: 
                            expression=expression.replace("(", "")
                            expression=expression.replace(")", "")                
                            phrasesTxts, termsTxts=set(),set()
                            terms, phrases=[],[]
                            for variable in expression.split(" AND "):                    
                                if(len(variable.split(" ")) >1):
                                    print("Searching for phrase: \'"+ variable+"\'")
                                    phrasesTxts |= set((Engine.phrasesearch(variable, txts, finvindex))) #search for a phrase
                                    phrases.append(variable)          
                                else:
                                    terms.append(variable) #creating a set of the sole terms

                            if(len(terms)>0):                         
                                print("Searching for term(s): \'"+ str(terms)+"\'") #search for a set of terms 
                                termsTxts |= (Engine.termsearch(terms, txts, finvindex))                    

                            if(len(phrasesTxts)>0 or len(termsTxts)>0):
                                if(len(phrasesTxts)>0 and len(termsTxts)>0):
                                    results |= (phrasesTxts).intersection(termsTxts)
                                    print("Found "+str(terms)+" and "+str(phrases))

                                    if(len(results)==0):
                                        print("No common results found between "+str(terms)+" and "+str(phrases))
                                    else:
                                        print("Showing common results between "+str(terms)+" and "+str(phrases))

                                elif(len(phrasesTxts)>0 and len(termsTxts)==0):
                                    results |= phrasesTxts
                                    print("Found "+str(phrases))
                                elif(len(phrasesTxts)==0 and len(termsTxts)>0):
                                    results |= termsTxts
                                    print("Found "+str(terms))
                            else:
                                print("Not found")                    

                                    
                        window["-TXT LIST-"].update(results) #print results           
                elif (event == "-TXT LIST-"):  # A file was chosen from the query results

                    listValues=list(window["-TXT LIST-"].GetListValues())
                    selectedValue=listValues[window["-TXT LIST-"].GetIndexes()[0]]

                    try:
                        for dirpath, dirnames, files in os.walk(PATH):
                            for file_name in files:
                                if(file_name==selectedValue):
                                    filePath = os.path.join(
                                        dirpath, selectedValue
                                    )       
                        
                        print("opening "+filePath)
                        os.startfile(filePath)
                    except Exception as d:
                        print(d)
                elif(event =="-HOWTOUSE-"): #user opens how_to_use
                    print("opening 'How To Use'")
                    try:
                        os.startfile(os.path.dirname(os.path.realpath(__file__))+"/how-to-use.pdf")
                    except Exception as e:
                        print(e)


                if (event == "Exit" or event == sg.WIN_CLOSED):
                    break

            window.close()
            break

        else: #if the inverted index does not exist in the program's directory, the program will load the data from the given PATH and create an index in the program's directory
            print("The inverted index "+indexName+" does not exist in this directory")
            
            #Load and save data in an inverted index 
            texts, words = Engine.load_data(PATH)
            Engine.saveInvIndex(indexName, os.path.dirname(os.path.realpath(__file__))+"/", texts, words)
