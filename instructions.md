# BMI 709 - Student Project

In this individual project you will design and implement your own biomedical
Shiny app from scratch based on what you have learned in class.

## STEP 1 - Project Proposal

### Topic - Motivation

Your project should be related to your academic or professional interests /
expertise and in the field of biomedical / health sciences.

You will need to provide at least the following information

- Description of the core app functionality
- Target audience and their need for an app like yours. Make sure to be specific
  enough to demonstrate the usefulness to people or specific tasks
- Intended use cases and benefits over alternative methods

_NOTE: An app that is just exploring a dataset without providing much other
functionality or benefit is not considered a very useful app_

Fill out the following sections of the README.md file before requesting approval

- Title: Can be working title
- Motivation & Background: See section above
- App Overview
  - One or more images or sketches of the app's layout
  - Annotate all UI elements by describing their function (i.e. add a text
    description to each image)
  - Make sure to show the content of each tab (use inserts or separate images)
  - You will replace the sketches with actual app screenshots once you finish
    the project
- User Guide: Instructions on how to use the app. _No need to complete this in
  the first step_
- References: Add any references that your work builds on and make sure to use
  proper formatting

_Note: the User Guide section does not have to be completed for the proposal_

## STEP 2 - Project Development

You will work on this project over the course of several weeks, incorporating
new features as you learn them in class. There will be no intermediate deadlines
or grading, but you can ask for input or feedback whenever you need it by
contacting the course staff.

- Create a new `app.R` or `app.py` in the root of the project
- You can organise all other code as you see fit (but see below how to organise
  your data)
- Update the `README.md` file as you go, and remember that this is about your
  app itself, so it should not mention or discuss this course
- Update the `.gitignore` as needed so you only commit relevant files

NOTE: We encourage you to create new Git branches when introducing new features
into your app, but make sure to merge them back into the main branch when they
are finished as this is the one that will be used for evaluation.

### Features

Your app will need to contain the following features:

- An intuitive layout with logical organisation of the various components
  - The layout needs to contain multiple tabs (this can be a nested component
    somewhere)
- Minimum of 5 user inputs
- Minimum of 4 reactive outputs
  - At least 1 of the outputs is an interactive plot
  - At least 1 output is an interactive data table
  - Note: to be considered interactive, we expect that user interaction triggers
    specific _server-side code_. For example, clicking in a plot should result
    in execution of a reactive function on the server, not just evoke a a
    built-in reaction like zooming in
- At least one piece of data that can be either exported (plot, table, ...) or
  imported (dataset)
- At least two elements in your app should be styled using Bootstrap classes or
  custom CSS

### Data

All project data **should be stored inside a folder called `data`** which you
create in the root folder of your project.

- Do not hardcode absolute paths to data in your scripts to ensure portability
- The data folder is already in the `.gitignore` file so none of its content
  will be committed to Git. Make sure to only put data in there, not any scripts
  or documentation (need to be committed).
- The static assets folder (e.g. `www`) is not part of the data folder and will
  be committed to the repo as it is part of the app layout

#### Sharing app data

If your project uses datasets that contain **sensitive or protected
information**, you should **never share** this. Generate dummy datasets such
that the functionality of the app can be demonstrated properly, but don't worry
too much about the results of any analysis being correct (it just needs to
display something for the demo)

You will receive a **link to upload your data separately** so we can run your
app as it was intended.

- The total size of the `data` folder (compressed) should be < 100 MB
- Remove and replace sensitive data before compressing!
- The `data` folder structure (e.g. if you have subfolders) should be preserved
  so references in your scripts won't break

To generate the data file to upload, run the function below which will tarball
and compress your `data` folder:

**R**

```r
tar(tarfile = "data.tar.gz", files = "data", compression = "gzip")
```

**Python**

```python
import tarfile
with tarfile.open("data.tar.gz", "w:gz") as tar:
    tar.add("data")
```

## STEP 3 - Hosting and Testing

Make sure your app is fully functional and the README has been updated

- Replace initial sketches with screenshots
- Add the User Guide (i.e. tutorial / additional info). You can create a
  separate folder with documentation if you like, and use the User Guide section
  to provide links to these (markdown) files
- Update references if needed
- Make sure to test you app from a clean install
  - Clone the repo from GitHub into a new folder
  - Unzip the `data.tar.gz` file to add the `data` folder
  - Run and test the app

You will host your app on your own laptop and be given feedback by your peers in
the final class session. Details on how to host apps locally will be shared
later.

## Grading

Check the course syllabus for details on grading

---

_This project is part of the BMI 709 course offered by the Master of Biomedical
Informatics at Harvard Medical School._
