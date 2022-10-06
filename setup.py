#!/usr/bin/env python

from setuptools import setup

with open('README.rst', encoding='utf-8') as readme_file:
    README = readme_file.read()


def read_requirements():
    with open('requirements.in', encoding='utf-8') as fobj:
        lines = [line.split('#', 1)[0].strip()
                 for line in fobj]
    # drop empty lines:
    return [line
            for line in lines
            if line and not line.startswith('#')]


INSTALL_REQUIRES = read_requirements()


setup(
    name='git-form-saver',
    version='0.0.4',
    description="Git form saver",
    long_description=README,
    author="Peter Demin",
    author_email='peterdemin@gmail.com',
    url='https://github.com/peterdemin/git-form-saver',
    packages=[
        'gitformsaver',
    ],
    package_dir={
        'gitformsaver': 'gitformsaver',
    },
    entry_points={
        'console_scripts': [
            'git-form-saver=gitformsaver.cli:run_http_server',
            'git-form-saver-jwt-token=gitformsaver.cli:generate_token',
        ]
    },
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    license="MIT license",
    zip_safe=False,
    keywords='git http form saver',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.10',
    ],
    test_suite='tests',
    python_requires='>=3.10',
    tests_require=['pytest'],
)
