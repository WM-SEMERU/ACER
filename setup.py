import setuptools

setuptools.setup(
    name='CallGraph',
    version='0.1.0',
    author='Call Graph',
    author_email='nacooper01@email.wm.edu',
    description='a package to generate call graphs and train them on graph neural networks',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/WM-SEMERU/CSci435-Fall21-CallGraph.git',
    install_requires=[
        'tree-sitter >= 0.19.0',
        'pandas >= 1.3.3',
        'gitpython >= 3.1.24'
    ],
	packages=['CallGraph'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ]
)