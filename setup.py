# Copyright (c) 2010-2015 Richard Lincoln. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from setuptools import setup, find_packages


setup(
    name='PYPOWER',
    version='5.1.19',
    author='Richard Lincoln',
    author_email='r.w.lincoln@gmail.com',
    description='Solves power flow and optimal power flow problems',
    long_description='\n\n'.join(
        open(f, 'rb').read().decode('utf-8')
        for f in ['README.rst', 'CHANGELOG.rst']),
    url='https://github.com/rwl/PYPOWER',
    license='BSD',
    install_requires=[
        # Deactivated to avoid problems with system packages.
        # Manual installation of NumPy and SciPy required.
        # 'numpy>=1.6',
        # 'scipy>=0.9',
    ],
    entry_points={'console_scripts': [
        'pf = pypower.main:pf',
        'opf = pypower.main:opf'
    ]},
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
    ],
)
