# pyretro

``` python

dependecies = [
    'python-dev',
    'libsdl-image1.2-dev',
    'libsdl-mixer1.2-dev', 
    'libsdl-ttf2.0-dev', 
    'libsdl1.2-dev', 
    'libsmpeg-dev',
    'python-numpy',
    'subversion',
    'libportmidi-dev',
    'ffmpeg',
    'libswscale-dev',
    'libavformat-dev',
    'libavcodec-dev'
]

def getting_started():
    try:
        run('pip install pygame')
        run('python space.py')

    except MissingDependecies:
        for package in dependecies:
            system.install(package)
        
        getting_started()
```