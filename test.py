# imports ----------------------------------------------------------------------
import time
import random
import speech_recognition as sr
import eliza

# classes ----------------------------------------------------------------------
# child class of Eliza to make it possible to rewrite the run method
class postbox(eliza.Eliza):
    # the run-loop (conversation)
    def run(self):
        said = ''
        repeat = True
        # repeat until no error has occured and something has been recognized
        while repeat:
            with sr.Microphone() as source: # listen to microphone
                audio = sr.listen(source)
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

        return True

# main script ------------------------------------------------------------------
posty = postbox()
posty.load('postbox.txt')

# main loop
while True:
    posty.run()
