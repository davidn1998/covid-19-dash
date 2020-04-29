from setuptools import find_packages, setup

setup(
    name='covid-19-dash',
    version='1.0.0',
    license='MIT',
    description='A dashboard displaying covid-19 data and visualizations',
    author='David Nwachukwu',
    author_email='davidnw1998@gmail.com',
    packages=find_packages(),
    include_pacakge_data=True,
    url='https://github.com/davidn1998/uni-share',
    keywords = ['COVID-19', 'DASHBOARD' ,'APP'],
    zip_safe=False,
    install_requires=[
        'requests',
        'pandas',
        'numpy',
        'dash',
        'plotly',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Topic :: Education',
        'License :: OSI Approved :: MIT License',
        'Framework :: Flask',
        'Programming Language :: Python :: 3', 
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
  ],
)