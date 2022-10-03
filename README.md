# curtana

Curtana - The Sword of Mercy and empathy. A tool that allows you to assist your students as they work through the labs.

### Sample output:

> Note that there is just one line per student:

```
LAB: 26  COUNTER: 2   enter: "live-gtg 26 " to report lab completed
Time now: 2022-10-03 15:06:52
                                                Suc-             Last Command
Class-ID          Student           Help  Cmds  cess  Fail  GTG   Timestamp      Seconds  Results + Latest Command
----------------- ----------------  ----- ----  ----  ----  ---  --------------  -------  ----------------------------------
json-pyb-18       seaneon                   32    28     4   26  Oct:2:21:43:17    77015  [  0] live-gtg 26
json-pyb-18       Jasper                     2     1     1   26  Oct:2:21:43:17    77015  [  0] live-gtg 26
```


### Tech behind the scenes, deep inside live.alta3.com
Curtana tails /var/log/student.logs.  So this raises the question, what is "/var/log/student.logs". The answer is that /var/log/student.logs is logging EVERYTHING that ALL students type on the command line. All log lines appear as follows:

```
Sep 1 16:06:44 bchd.a89b5f49-0b1b-4387-905e-5cf330f8095a student: student@bchd:/home/student$ sudo apt install python3-pip -y [0]
```

Curtana then parses eacch log entry and generates the following dictionary items:


```
{
     "month": str
       "day": str
     "hours": str
     minutes: str
     seconds: str
    "domain": str # "bchd.a89b5f49-0b1b-4387-905e-5cf330f8095a"
      "user": str
    "prompt": str
    "command: str # Parsing this command allows some cool magic. See Parsed CLI commands below 
    "result": str  #[0]"
}
```

Certian CLI commands are parsed to add considerable power to curtana:

### Parsed CLI commands:
# --------------------------------------------------------
```
#1 The INSTRUCTOR assigns newly spun up instances to a class_id
Assign Class name:    live-class-id string
               ie:    live-class-id jason-18pyb

#2 Each student maps their environment to their name
Assign student name:  git config --global user.name name
                 ie:  git config --global user.name seaneon

#3 An instructor uses the following to make a lab assignment to the class:
Lab assignment:       live-lab # student-tracker class_id  
            ie:       live-lab 6 student-tracker jason-pyb18

#4 Students report progress on assigned lab as follows. ONLY works when the lab is assigned.
Lab completion:       live-gtg lab#
            ie:       live-gtg 6

#5 A student cries out for help
Request lab help:     live-help lab# step#
              ie:     live-help 20   14 

#6 A student (or instructor) clears the request for help
Clear Lab Help:       live-help clear
```

curtana supporting bash scripts
- live-help
- live-gtg
- live-class-id
- live-lab
- live  (A help script for the live suit)****
