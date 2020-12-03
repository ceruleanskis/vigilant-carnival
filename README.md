# vigilant-carnival

vigilant-carnival (not a real name, the game is currently untitled so this is just a codename)
is a sci-fi roguelike developed with python 3.9 and [pygame](https://github.com/pygame/pygame).
## Getting Started

These instructions will get you a copy of the project up and running on your 
local machine for development and testing purposes.
 
See build for notes on how to build the project to an executable, and how to build the docs.

### Prerequisites

What things you need to install the software and how to install them

```
python v3.9
```

### Installing

Create a virtual environment for python, and install the requirements via pip.
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running the game

Once the requirements are installed, from your venv, run from the main directory:

```
python main.py
```

## Running the tests

vigilant-carnival uses python's [unittest](https://docs.python.org/3/library/unittest.html) framework for tests. To run them:

```
python -m unittest
```

## Build

### Building the docs

vigilant-carnival uses [sphinx](https://github.com/sphinx-doc/sphinx) for generating documentation.

To build, run:

```
./build-docs
``` 

alternatively:

```
cd docs
make html
cd ..
sphinx-apidoc -o docs/source/ .
```

With either of these methods, the docs site will output to `docs/build`.

Start an http server of your choice and navigate to `index.html` to read the docs.

Example:
```
cd docs/build
python -m http.server # site is available at http://localhost:8000/
```
### Building the game executable

vigilant-carnival uses 
[PyInstaller](https://github.com/pyinstaller/pyinstaller/) to bundle the application.

The PyInstaller spec file is located at `mygame.spec`.

To build, run:

```
./build-pyinstaller
```

alternatively:

```
pyinstaller mygame.spec -y --clean -n "mygame" --onefile
```

Using either of these methods, the executable will be created at `dist/mygame`.

## Built With

* [pygame](https://github.com/pygame/pygame) - library utilizing SDL for video game development
* [PyInstaller](https://github.com/pyinstaller/pyinstaller/) - Used to bundle executable
* [sphinx](https://github.com/sphinx-doc/sphinx) - Used to generate documentation

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/ceruleanskis/vigilant-carnival/releases). 

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

