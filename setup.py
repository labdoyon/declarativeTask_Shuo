from setuptools import setup, find_packages

setup(
    name='declarativeTask3_ShuoExperience',
    version='2021.10',
    description='a declarative memory task',
    # long_description="""""",
    url='https://github.com/ThibaultVlieghe/declarativeTask_Shuo',
    author='Thibault Vlieghe (current), Arnaud Boré (original)',
    # author_email='author@example.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Scientists',
        'Topic :: declarative memory :: Sleep :: memory reactivation :: memory manipulation',
        'License :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='memory, declarative, sleep, reactivation',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6, <=3.9.5',
    # install_requires=[],
    # entry_points={  # Optional
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
    # project_urls={  # Optional
    #     'Bug Reports': '',
    #     'Funding': '',
    #     'Say Thanks!': '',
    #     'Source': 'https://github.com/ThibaultVlieghe/declarativeTask_Shuo',
    # },
)
