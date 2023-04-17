# PickingComics
Picking comics from a website.

## Introduction
This a simple program for picking comics from [dmzj](https://manhua.dmzj.com/). After running this program, you can obtain a pdf file with contents you like. 

What you need  is listed below:
- Chromium Browser or Chrome Browser 
- ChromeDriver(you can download [here](https://chromedriver.chromium.org/downloads))
- poetry

## Usage
### Install Package 
This program depends on these packages: `requests` `lxml` `selenium` `pillow` `fpdf`. You can install them by pip, however, this project is created by poetry and you can use `poetry install` to install all packages this project needed.

### Picking Comics
Firstly, you should go to the [dmzj](https://manhua.dmzj.com/) and select a url of a commic, it maybe like this: http://manhua.dmzj.com/bianfuxiazhimingwanxiao/. And then, you can just start the 'main.py' and enter the url when the program show you 'enter url'. 

After that, the browser will open and download pictures for you, and you will get a pdf file in the directory where 'main.py' is located.
