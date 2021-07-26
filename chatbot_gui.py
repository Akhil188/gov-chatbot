from tkinter import *
import time
import tkinter.messagebox
import threading
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import os
from googletrans import Translator
from langdetect import detect
import json 
import numpy as np
from tensorflow import keras

import tensorflow as tf
import random
import pickle

with open("C:/Users/Akhil/Desktop/govtbot/intents.json",encoding="utf8") as file:
    data = json.load(file)

model = keras.models.load_model('chat_model')
    
    # load tokenizer object
with open('C:/Users/Akhil/Desktop/govtbot/tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

    # load label encoder object
with open('C:/Users/Akhil/Desktop/govtbot/label_encoder.pickle', 'rb') as enc:
    lbl_encoder = pickle.load(enc)

saved_username = ["You"]
#ans=["PyBot"]
window_size="400x400"

class ChatInterface(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master

        # sets default bg for top level windows
        self.tl_bg =  "#1c2e44"
        self.tl_bg2 ="#263b54"
        self.tl_fg ="#FFFFFF"
        self.font = "Arial 10"

        menu = Menu(self.master)
        self.master.config(menu=menu, bd=5)
# Menu bar

    # File
        file = Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file)
       # file.add_command(label="Save Chat Log", command=self.save_chat)
        file.add_command(label="Clear Chat", command=self.clear_chat)
      #  file.add_separator()
        file.add_command(label="Exit",command=self.chatexit)
    
     # username
  
        help_option = Menu(menu, tearoff=0)
        menu.add_cascade(label="Help", menu=help_option)
        #help_option.add_command(label="Features", command=self.features_msg)
        help_option.add_command(label="About PyBot", command=self.msg)
        help_option.add_command(label="Develpoers", command=self.about)

        self.text_frame = Frame(self.master, bd=6)
        self.text_frame.pack(expand=True, fill=BOTH)

        # scrollbar for text box
        self.text_box_scrollbar = Scrollbar(self.text_frame, bd=0)
        self.text_box_scrollbar.pack(fill=Y, side=RIGHT)

        # contains messages
        self.text_box = Text(self.text_frame, yscrollcommand=self.text_box_scrollbar.set, state=DISABLED,
                             bd=1, padx=6, pady=6, spacing3=8, wrap=WORD, bg=None, font="Verdana 10", relief=GROOVE,
                             width=10, height=1)
        self.text_box.pack(expand=True, fill=BOTH)
        self.text_box_scrollbar.config(command=self.text_box.yview)

        # frame containing user entry field
        self.entry_frame = Frame(self.master, bd=1)
        self.entry_frame.pack(side=LEFT, fill=BOTH, expand=True)

        # entry field
        self.entry_field = Entry(self.entry_frame, bd=1, justify=LEFT)
        self.entry_field.pack(fill=X, padx=6, pady=6, ipady=3)
        # self.users_message = self.entry_field.get()

        # frame containing send button and emoji button
        self.send_button_frame = Frame(self.master, bd=0)
        self.send_button_frame.pack(fill=BOTH)

        # send button
        self.send_button = Button(self.send_button_frame, text="Send", width=5, relief=GROOVE, bg='white',bd=1,
                                   command=lambda: self.send_message_insert(None), activebackground="#1c2e44",
                                  activeforeground="#FFFFFF")
        self.send_button.pack(side=LEFT, ipady=8)
        self.master.bind("<Return>", self.send_message_insert)
        
        self.last_sent_label(date="No messages sent.")
        #speech button
        
        self.speech_button = Button(self.send_button_frame, text="Speech", width=5, relief=GROOVE, bg='white',
                                  bd=1, command=lambda:self.speech(), activebackground="#263b54",
                                  activeforeground="#000000")
        self.speech_button.pack(side=LEFT, ipady=8)
        
        #refresh
       
        
        self.master.config(bg="#263b54")
        self.text_frame.config(bg="#263b54")
        self.text_box.config(bg="light yellow", fg="black")
        self.entry_frame.config(bg="#263b54")
        self.entry_field.config(bg="#263b54", fg="white", insertbackground="#FFFFFF")
        self.send_button_frame.config(bg="#263b54")
        self.send_button.config(bg="#1c2e44", fg="#FFFFFF", activebackground="#1c2e44", activeforeground="#FFFFFF")
        self.speech_button.config(bg="#1c2e44", fg="#FFFFFF", activebackground="#1c2e44", activeforeground="#FFFFFF")
        self.sent_label.config(bg="#263b54", fg="#FFFFFF")

        self.tl_bg = "#1c2e44"
        self.tl_bg2 = "#263b54"
        self.tl_fg = "#FFFFFF"

        #t2 = threading.Thread(target=self.send_message_insert(, name='t1')
        #t2.start()
        
    
    def playResponce(self,responce,langg):
        speak = gTTS(text=responce, lang=langg, slow= False)  
        speak.save("captured_voice.mp3")     
        playsound('.\captured_voice.mp3')
        os.remove("captured_voice.mp3")
        
        
    def last_sent_label(self, date):

        try:
            self.sent_label.destroy()
        except AttributeError:
            pass

        self.sent_label = Label(self.entry_frame, font="Arial 7", text=date, bg=self.tl_bg2, fg=self.tl_fg)
        self.sent_label.pack(side=LEFT, fill=X, padx=3)

    def clear_chat(self):
        self.text_box.config(state=NORMAL)
        self.last_sent_label(date="No messages sent.")
        self.text_box.delete(1.0, END)
        self.text_box.delete(1.0, END)
        self.text_box.config(state=DISABLED)

    def chatexit(self):
        exit()

   
    def msg(self):
        tkinter.messagebox.showinfo('Government schemes chatbot')

    def about(self):
        tkinter.messagebox.showinfo("PyBOT Developers","1.Keerthana\n2.Dhruthi\n3.GowriNagh")
    
    def send_message_insert(self, message):
        
        user_input = self.entry_field.get()
        if(user_input==''):
            pr1 = "You: " + message + "\n"
            query=message
        else:
            pr1=pr1 = "You: " + user_input + "\n"
            query=user_input
        
        language=detect(query)
        if(language!='te'):
            language='en'
        
        translator = Translator()
        translation = translator.translate(query, dest='en')
        
        self.text_box.configure(state=NORMAL)
        self.text_box.insert(END, pr1)
        self.text_box.configure(state=DISABLED)
        self.text_box.see(END)
        #t1 = threading.Thread(target=self.playResponce, args=(user_input,))
        #t1.start()
        #time.sleep(1)
        ans=self.chat(translation.text)
        
        if(ans==None):
            ans="See you again..."
        
        translator = Translator()
        translation = translator.translate(ans, src='en' , dest=language)
        
        print(translation.text)
        pr="Bot : " + translation.text + "\n"
        self.text_box.configure(state=NORMAL)
        #if(language=='en'):
         #   self.text_box.insert(END, pr)
        #else:
         #   ob=self.translating(ob)
            #pr="Bot : " + ob + "\n"
        self.text_box.insert(END, pr)
        self.text_box.configure(state=DISABLED)
        self.text_box.see(END)
        self.last_sent_label(str(time.strftime( "Lastmessage sent: " + '%B %d, %Y' + ' at ' + '%I:%M %p')))
        self.entry_field.delete(0,END)
        if(user_input==''):
            self.playResponce(translation.text,language)
        else:
            if(ans!=None):
                t1 = threading.Thread(target=self.playResponce,args=(translation.text,language))
                t1.start()
            
            
    
    def chat(self,inp):
         max_len = 20
         result = model.predict(keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([inp]),
                                             truncating='post', maxlen=max_len))
         tag = lbl_encoder.inverse_transform([np.argmax(result)])
         for i in data['intents']:
             if i['tag'] == tag:
                 return np.random.choice(i['responses'])
        
        #return ob      
    def translating(self,message):
        translator = Translator()
        translation = translator.translate(message, src='en' , dest=language)
        return translation.text
        
    def speech(self):
        self.ins_label = Label(self.text_box, font="Verdana 7", text="For telugu say 'TELUGU'...For english say 'ENGLISH' ", bg=self.tl_bg2, fg=self.tl_fg)
        self.ins_label.pack(side=TOP, fill=X)
        def callback():
            lang='en'
            r = sr.Recognizer()        
            while(1):           
    # Exception handling to handle 
    # exceptions at the runtime 
                try:           
        # use the microphone as source for input. 
                    with sr.Microphone() as source2:               
            # wait for a second to let the recognizer 
            # adjust the energy threshold based on 
            # the surrounding noise level  
                        r.adjust_for_ambient_noise(source2, duration=0.2)               
            #listens for the user's input  
                        audio2 = r.listen(source2) 
            # Using google to recognize audio 
                        MyText = r.recognize_google(audio2, language=lang) 
                        MyText = MyText.lower() 
                        print(MyText)
                        if(MyText=='telugu'):
                            lang='te'
                        elif(MyText=='ఇంగ్లీష్'):
                            lang='en'
                        
                        self.send_message_insert(MyText)
                        
                        #print(ob)
                        if(MyText=='quit' or MyText=='క్విట్'):
                            break
                                                                              
                        
              
                except sr.RequestError as e: 
                    print("Could not request results; {0}".format(e))            
          
                except sr.UnknownValueError: 
                    print("no query")
                
        
        t = threading.Thread(target=callback)
        t.start()
        
root=Tk()
a = ChatInterface(root)
root.geometry(window_size)
root.title("Bot")
root.mainloop()