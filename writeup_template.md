# Project: Search and Sample Return
## Project goals
### Training / Calibration
* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

### Autonomous Navigation / Mapping
* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook).
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands.
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.  

[//]: # (Image References)

[rock1_processed]: ./misc/example_rock1_processed.png
[grid1_processed]: ./misc/example_grid1_processed.png
[rover_dir1]: ./misc/rover_direction1.png
[rover_dir2]: ./misc/rover_direction2.png
[rover_dir3]: ./misc/rover_direction3.png

## [Rubric Points](https://review.udacity.com/#!/rubrics/916/view)
Below I will consider the rubric points individually and describe how I addressed each point in my implementation.  
### Writeup

1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.

You're reading it!

### Notebook Analysis
1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.
Extra: grab extra values from CSV and fill dataset, show them in the image, show rover vision too.

2. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result.
And another!


In order to identify navigable terrain, obstacles or rocks from one of the rover's camera shots, the `process_image()` function has been modify to filter pixels within a given range. Not only pixels with a value bigger than X are selected, but also pixels with a value between X and Y. This translates into passing a bottom and a top thresholds as parameters to the function.

* Navigable terrain: only the bottom threshold is used (the given value of 160 is used).
* Obstacles: the opposite of navigable terrain.
* Rocks: Since the rocks are yellow, most of the filter happens in the red and green channels (red plus green equals yellow). Rocks have also a small dark blue component.

![Rock 1][rock1_processed]

![Grid 1][grid1_processed]

As an example on how to use the Jupyter Notebook to test and improve the image processing, [this video](./misc/test_pitch_yaw_selection.mp4) has been included in the repository. The goal of that video was to check which ranges of the pitch and yaw angles to use for discarding shots where the grid was not calibrated. These values have been extracted from the CSV and inserted into the dataset.

The Notebook has also been used to tune the rover's direction. In order to navigate near the wall, we point it to the minimum angle obtained after the transformation to polar coordinates (to navigate near the right hand wall). We add an offset because the edges are a bit irregular, which makes the image is not stable.

We also calculate how many navigable pixels are if we point the rover towards the aforementioned direction.

![Direction 1][rover_dir1]

![Direction 2][rover_dir2]

![Direction 3][rover_dir3]

### Autonomous Navigation and Mapping

1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**

| Resolution |  Quality  |
|------------|-----------|
|  1280x720  |  Fastest  |

I have modified the given decisions tree to obtain more accurate results. The following modifications were enough to map at least 80% of the map with a 60% accuracy:
* Don't throttle if the required steering angle is too big and the speed is already big enough. The reason I do this is because the higher the steering angle and the speed are, the further from 0 pitch and roll will be. In this case, a lot of the captured images would have to be discarded for not accurate enough for mapping with our grid calibration. Reducing the speed (or at least not increasing it), will result in more valid shots.
* Continue in stop mode until the camera sees navigable terrain and the required steering angle to reach it is not bigger than what the rover can steer (+/-15º).

I have added to extra modes (unstuck and sample) to the two existing ones (forward and stop).
* Unstuck: when the rover is in this mode, it will move backwards during some meters and then go back to forward mode. To allow the rover to start moving, this mode can only be entered when a flag called `started` has been set. This is set whenever the robot exceeds certain speed.
* Sample: whenever the flag `near_sample` is set, the rover goes into this mode and sends a pick up order. The mode is left after when `picking_up` is `False`.

Some ideas to improve the results are:
* I am under the impression that the areas supposed to be shadows are not being properly detected as navigable terrain. This could be fixed spending some extra time on fine tuning the image thresholds. This would allow the rover by to navigate even closer to the wall and thus pick more samples and increase the map's fidelity.
* Smarter unstuck algorithm. Some of the rocks found in the middle of the navigable terrain block the rock from moving in any direction. 
