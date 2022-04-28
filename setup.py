import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='query-counter',
    version='0.1.0',
    install_requires=['SQLAlchemy>=1.4.31'],
    packages=setuptools.find_namespace_packages(),
    url='https://github.com/tatari-tv/query-counter',
    license='MIT',
    author='brian-tatari',
    author_email='brian.olecki@tatari.tv',
    description='SQLAlchemy model N+1 debugger',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='query counter debugger n+1 sqlalchemy',
)
