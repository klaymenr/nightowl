# NightOwl - IR Cut validate program

This repo contains 2 applications, `grabber` and `scanner`.  These are off-line
test tools, which means we need to do ircut filter testing for an amount of
time, then we can do image analyzing. Testing/Analyzing process is separated.

## grabber
Downloading JPEGs from camera and alteranting IRCut filter

### usage

Run `grabber` to start testing IRcut. If nothing given, it will use default
settings to test.  Configs could be given by CLI or config file.  If there is a
config file called `grabber.ini` exists in the same folder, `grabber` will use
it as parameter, and ignore all CLI parameters.  Refer `grabber.ini` for config
sample. So if `grabber.ini` is prepared, the user just need to double-click
program icon to start grabbing/testing camera.

Once `grabber` started, it will do continusly ircut filter switching and
snapshot downloading for specified iterations.  A transition of `day -> night
-> day` is considered as an iteration.


#### CLI usage

Tell `grabber` to test camera ircut at <ip>, images will be written to
`grabbed_images`.
```
grabber <ip> 
```

Tell `grabber` to test camera ircut for `500` iterations at <ip>, images will
be written to `grabbed_images`.
```
grabber <ip> -i 500
```

Tell `grabber` to test camera ircut for `500` iterations at <ip>, images will
be written to `<what_ever_you_like>`.
```
grabber <ip> -o <what_ever_you_like>
```

## scanner
Analyzing JPEGs to find out possible ircut filter stucked images.

### usage

`scanner` will recursively search files ends with `.jpeg` or `.jpg`, calculate
score of ircut stuck of an image and output into `output.html`.  Default
searching folder is `grabbed_images`.  The content of `output.html` is sorted
by `score`, you could check from file which has highest score.

By default, `scanner` will computing score by assuming ircut filter moving in
horizontal direction.  However some devices have vertical moving ircut filter.
In this case, you could provide `-d` to specify ircut moving direction.

