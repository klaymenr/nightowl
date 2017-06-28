# NightOwl - IR Cut validate program

This repo contains 2 applications, `scanner` and `grabber. 

## scanner
Program analyzing JPEGs to find out ircut filter stucked images

### usage

Run `scanner` will recursively search files ends with `.jpeg` or `.jpg`,
calculate score of ircut stuck of an image and output into `output.html`.  The
content of `output.html` is sorted by `score`, you could check from file which
has highest score.

In theory, ircut moving direction should be horizontal, which can reduce
fraction on moving since the ircut doesn't affected by gravity.  However some
devices do moving their ircut in vertical direction, which `scanner` needs to
know when computing `score` of an iamge, so `scanner` provides `-d` to specify
ircut moving direction. If your device


## grabber
Program for downloading JPEGs from camera and alterantes IRCut status

### usage
Just run `grabber` with IP provided will start testing IRcut, default iteration
is 5000, which means the testing device will switch day/night for 5000 times. A
`day -> night -> day` counted as 1 switch.

```
grabber <ip> 
```

You can change iteration by `-i <iteration>`, say we'd like to test for `500` times
```
grabber <ip> -i 500
```

Images downloaded will be put to `grabbed_images` by default, which could be
changed by providing `-o` when running `grabber`, like: 
```
grabber <ip> -o <what_ever_you_like>
```

