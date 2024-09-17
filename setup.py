from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name = 'bgcombine',
    version = '1.2.10',
    author = 'Dominic Miller',
    author_email = 'dommiller88@gmail.com',
    license = 'MIT',
    description = 'BGC Combiner is a tool for transforming and combining data from ProCare.',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/dommiller88/bgcombine',
    py_modules = ['my_tool', 'app'],
    packages = find_packages(),
    install_requires = [requirements],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    entry_points = '''
        [console_scripts]
        bgcombine=my_tool:main
    '''
)
