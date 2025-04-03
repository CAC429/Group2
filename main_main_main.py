import subprocess

tc_process = subprocess.Popen(["python", "uiscript.py"])
tm_process = subprocess.Popen(["python", "Main_Train_Model.py"])

tc_process.wait()
tm_process.wait()

#Brakes work in decelerating the train, but now when the brakes are released the train doesn't accelerate to the suggested speed
# because train model doens't handle suggested speed/authority

#Hard coded suggested speed to be 20
#change time function from 0.1 seconds to 1 second

#Need to code beacon data