# curtana

Curtana - The Sword of Mercy and empathy. A tool that allows you to assist your students as they work through the labs.

### Sample output:

> Note that there is just one line per student:

```
LAB: 26  COUNTER: 2   enter: "live-gtg 26 " to report lab completed
Time now: 2022-10-03 11:05:20
Class-ID      Student       Help  Cmds  Success Fail  Last Command    Seconds  Results + Latest Command
------------- ------------  ----- ----- ------- ----  --------------  -------  ----------------------------------
json-pyb-18   seaneon               31      27     4  Oct:2:21:43:17       75  [  0] live-lab 26 student-tracker jason-pyb-18
json-pyb-18   alfred         20-6    1       0     1  Oct:2:21:43:41      120  [  2] ls deleteme.py
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
    "command: str # Parsing this command allows some cool magic. See Parsed CLI command below 
    "result": str  #[0]"
}
```

Certian CLI commands are parsed to add considerable power to curtana:

### Parsed CLI commands:
# --------------------------------------------------------
```
Lab assignment:       live-lab # student-tracker class_id
            ie:       live-lab 6 student-tracker jason-18-pyb

Request lab help:     live-help lab# step#
              ie:     live-help 20   14 

Clear Lab Help:       live-help clear

Assign student name:  git config --global user.name name
                 ie:  git config --global user.name seaneon

Assign Class name:    live-class-id string
               ie:    live-class-id jason-18-pyb

Lab completion:       live-gtg lab#
            ie:       live-gtg 25
```
