from distutils.core import setup
setup(
    name='QExPy',
    packages=['QExPy'],
    version='1.2.2.dev8',
    description='''Objects to handle calculations with uncertainty and
    plotting with a focus on use in physics.''',
    author='Connor Kapahi',
    author_email='connorkapahi@gmail.com',
    license='MIT',
    url='https://github.com/Queens-Physics/qphyssy',
    download_url='https://github.com/Queens-Physics/qphyssy/tarball/0.1',
    keywords=['physics', 'undergrad', 'queens', 'university', 'analysis',
                'uncertainty', 'plotting'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
    install_requires=['numpy', 'scipy'],
)