# imports ----------------------------------------------------------------------
import speech_recognition as sr
import pyttsx3
import eliza

# objects ----------------------------------------------------------------------
r = sr.Recognizer()
engine = pyttsx3.init()

# set properties of text to speech voice
engine.setProperty('rate', 110) # words per minute
engine.setProperty('volume', 1.0) # volume

# classes ----------------------------------------------------------------------
# child class of Eliza to make it possible to rewrite the run method
class postbox(eliza.Eliza):
    def run(self):
        # print and speak greeting
        intro = self.initial()
        print(intro)
        engine.say(intro)
        engine.runAndWait()

        # main loop
        while True:
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
                break

            # print and speak answer
            print(output)
            engine.say(output)
            engine.runAndWait()

        # print and speak goodbye
        outro = self.final()
        print(outro)
        engine.say(outro)
        engine.runAndWait()

# main script ------------------------------------------------------------------
therapist = postbox()
therapist.load('postbox.txt')
therapist.run()
