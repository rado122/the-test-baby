from setuptools import setup, find_packages

requires = [
    "colorlog>=3.1.4",
    "faust==1.8.1",
    "robinhood-aiokafka==1.0.5",
    "simple-settings>=0.16.0"
]

setup(
    name='tide_test',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'tide_test = tide_test.app:main',
        ]
    },
)
