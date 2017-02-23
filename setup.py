from setuptools import setup, find_packages
 
setup(
        
    name="Policosm",
    version="0.1",
    packages=find_packages(),

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    
    requires=[
        "shapely",
        "geojson",
        "numpy",
        "networkx",
        "rtree",
        "matplotlib"
        "descartes"
        "colorlover", 
        "plotly", 
        "imposm", 
        "sklearn",
        "osgeo",
        "rdp"
    ]

    install_requires=[
        "shapely",
        "geojson",
        "numpy",
        "networkx",
        "rtree",
        "matplotlib"
        "descartes"
        "colorlover", 
        "plotly", 
        "imposm", 
        "sklearn",
        "osgeo",
        "rdp"
    ],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author="Fabien Pfaender",
    author_email="fabien.pfaender@me.com",
    description="a library to extract, explore, analyze and draw osm based extracts. Convert osm maps into graphs, networks, and polygons",
    license="MIT License",
    keywords="openstreetmap osm graph extractor analysis spatial",
    url="https://github.com/ComplexCity/policosm",   # project home page, if any

    classifiers=(
        "Development Status :: 1 - Pre-Alpha"
        "Intended Audience :: Developers"
        "Natural Language :: English"
        "Programming Language :: Python"
        "Programming Language :: Python :: 2.7"
        "Topic :: Software Development :: Libraries :: Python Modules"
    ),
)