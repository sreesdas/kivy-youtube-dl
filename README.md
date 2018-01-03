# Kivy Youtube-DL
A youtube video downloader made with **Kivy and Kivy-MD** powered by **pyTube**.
Supported platforms : Windows, Linux, Mac and Android


## Getting Started

Download the zip or Clone the repo to start working with this project. 

* **Desktop** : Run the main.py inside the project folder.
* **Android** : Install kivy launcher from playstore, copy the project folder into the kivy folder(if exists otherwise create a new one) in the sdcard.

	Copy paste the URL into the TextField and select one from the available formats.

If you have any feedback or run into issues, please file an issue on this repository.

### Prerequisites

* Python (2.7)
* Kivy ( >1.9.0 required)
* Kivy-MD
* PyTube
* Buildozer (optional)

### Installing

* Before installing Kivy, you have to install the dependencies first

```
$ python -m pip install --upgrade pip wheel setuptools
$ python -m pip install docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew
$ python -m pip install kivy.deps.gstreamer
```
* Now install kivy and kivy sample projects

```
$ python -m pip install kivy
$ python -m pip install kivy_examples
```

* Install kivy-md by cloning the project and run the setup.py file

```
$ git clone https://gitlab.com/kivymd/KivyMD.git
$ cd KivyMD
$ sudo python ./setup.py install
```
* Now the final step is to install pytube

```
$ pip install pytube
```


## Compiling the program as an Android App

Use buildozer for compilation.



## Authors

* **Sreenath Sivadas** - *Initial work* - [sreesdas](https://github.com/sreesdas)

See also the list of [contributors](https://github.com/sreesdas/project/contributors) who participated in this project.

## License

This project is licensed under the GPL License - see the [LICENSE.md](LICENSE.md) file for details

