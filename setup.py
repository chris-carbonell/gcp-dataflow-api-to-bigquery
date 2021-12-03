import setuptools

requires = [
            'apache_beam[gcp]',
            'google-cloud==0.34.0',
            'requests>=2.0',
            ]

setuptools.setup(
    name='api-to-bq-df',
    version='0.0.1',
    install_requires=requires,
    packages=setuptools.find_packages(),
)
