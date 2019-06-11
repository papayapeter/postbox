import subprocess
import speech_recognition as sr

input = ''

# function for getting command output as string (and waiting for the command to finish)
def command_wait(command):
    child = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    child.wait()
    output = child.communicate()[0]
    return output.decode()

# obtain audio from the microphone
r = sr.Recognizer()
with sr.Microphone() as source:
    print('Say something!')
    audio = r.listen(source)

try:
    input = r.recognize_sphinx(audio)
    print('Speech Recognition thinks you said ' + input)
except sr.UnknownValueError:
    print('Speech Recognition could not understand audio')
except sr.RequestError as e:
    print('Could not request results from Speech Recognition service; {0}'.format(e))

command_wait('espeak ' + '\"' + input + '\"')
