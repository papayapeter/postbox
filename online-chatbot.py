# imports ----------------------------------------------------------------------
import os
import speech_recognition as sr
from gtts import gTTS
import eliza

# objects ----------------------------------------------------------------------
r = sr.Recognizer()

# classes ----------------------------------------------------------------------
# child class of Eliza to make it possible to rewrite the run method
class postbox(eliza.Eliza):
    def run(self):
        # print and speak greeting
        intro = self.initial()
        print(intro)
        engine = gTTS(intro)
        engine.save('response.mp3')
        os.system('mpg123 response.mp3')

        # main loop
        while True:
            said = ''
            repeat = True
            # repeat until no error has occured and something has been recognized
            while repeat:
                with sr.Microphone() as source: # listen to microphone
                    audio = r.listen(source)
                try: # try to recognize
                    said = r.recognize_google(audio)
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
                break

            # print and speak answer
            print(output)
            engine = gTTS(output)
            engine.save('response.mp3')
            os.system('mpg123 response.mp3')

        # print and speak goodbye
        outro = self.final()
        print(outro)
        engine = gTTS(outro)
        engine.save('response.mp3')
        os.system('mpg123 response.mp3')

# main script ------------------------------------------------------------------
therapist = postbox()
therapist.load('postbox.txt')
therapist.run()
