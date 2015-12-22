from setuptools import setup, find_packages
setup(
    name="DftTraffic",
    version="2.0",
    packages=find_packages('DftTraffic'),  # include all packages under src
    package_dir={'':'DftTraffic'},   # tell distutils packages are under src
    install_requires = ['requests', 'cherrypy'],
    package_data={
        # If any package contains *.txt files, include them:
        #'': ['*.txt'],
    }
)
