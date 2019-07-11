# imports ----------------------------------------------------------------------
import os
import time
import random
import speech_recognition as sr
import eliza

# settings ---------------------------------------------------------------------
conversation_length = 10 # number of exchanges (+/- 20 % each time)

# objects ----------------------------------------------------------------------
r = sr.Recognizer()

# classes ----------------------------------------------------------------------
# child class of Eliza to make it possible to rewrite the run method
class postbox(eliza.Eliza):
    def say(self, text, rate, volume, voice = 'm1', filename = 'response.wav'):
        os.system('espeak \"' + text +
                  '\" -a ' + str(volume) +
                  ' -s ' + str(rate) +
                  ' -ven+' + voice +
                  ' -w ' + filename +
                  ' && aplay ' + filename)
    # call out
    def call(self):
        calls = ('Hello', 'Heeeeello', 'Anyone there?', 'I\'m a little lonely')
        call =  random.choice(calls)
        print(call)
        self.say(call, 110, 100)
    # thanks for the post
    def post_in(self):
        calls = ('Yummy. Mail', 'Thanks', 'Somebody will be happy')
        call =  random.choice(calls)
        print(call)
        self.say(call, 110, 100)
    # enjoy the post
    def post_out(self):
        calls = ('I feel a little empty now', 'oh', 'I hope it\'s good news')
        call =  random.choice(calls)
        print(call)
        self.say(call, 110, 100)
    # enjoy the post
    def post_out(self):
        calls = ('I feel a little empty now', 'oh', 'I hope it\'s good news')
        call =  random.choice(calls)
        print(call)
        self.say(call, 110, 100)
    # the goodbye
    def goodbye(self):
        calls = ('Have a wonderful day', 'goodbye then', 'please come visit me again')
        call =  random.choice(calls)
        print(call)
        self.say(call, 110, 100)
    # the greeting
    def initial(self): # print and speak greeting
        intro =  random.choice(self.initials)
        print(intro)
        self.say(intro, 110, 100)
    # the unlocking sentence
    def final(self): # print and speak goodbye
        outro = random.choice(self.finals)
        print(outro)
        self.say(outro, 110, 100)
    # the run-loop (conversation)
    def run(self):
        said = ''
        repeat = True
        # repeat until no error has occured and something has been recognized
        while repeat:
            with sr.Microphone() as source: # listen to microphone
                audio = r.listen(source)
            try: # try to recognize
                said = r.recognize_sphinx(audio)
                print('> ' + said)
                repeat = False
            except sr.UnknownValueError: # handle errors. repeat
                print('Speech Recognition could not understand audio')
            except sr.RequestError as e: # handle errors. repeat
                print('Could not request results from Speech Recognition program; {0}'.format(e))
            if said == '': # nothing detected. repeat
                print('No speech detected')

        # get response. exit if no response left
        output = self.respond(said)
        if output is None:
            return False

        # print and speak answer
        print(output)
        self.say(output, 110, 100)

        return True

# variables --------------------------------------------------------------------

# functions --------------------------------------------------------------------
def touched(): # what to do if touched
    # greeting
    posty.initial()

    # talk for conversation_length +/- 20%
    count = conversation_length + random.randint(-(conversation_length * 0.2), conversation_length *0.2)
    while count > 0 and posty.run():
        count -= 1

    # goodbye
    posty.final()

    # *** unlock

# main script ------------------------------------------------------------------
posty = postbox()
posty.load('postbox.txt')

# main loop --------------------------------------------------------------------
while True:
    if True: # *** touch condition instead of 'True'
        touched()
        # *** save mail state (is mail in the box?)
        # *** save unlocked state
    elif True: # *** take out condition & unlocked state & mail state instead of 'True'
        posty.post_out()
    elif True: # *** put in condition & unlocked state & mail state instead of 'True'
        posty.post_in()
    elif True: # *** cloed condition instead of 'True'
        posty.goodbye()
