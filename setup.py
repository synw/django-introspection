from setuptools import setup, find_packages


version = __import__('introspection').__version__

setup(
    name='django-introspection',
    packages=find_packages(),
    include_package_data=True,
    version=version,
    description='Introspection tools for Django',
    author='synw',
    author_email='synwe@yahoo.com',
    url='https://github.com/synw/django-introspection',
    download_url='https://github.com/synw/django-introspection/releases/tag/' + version,
    keywords=['django'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=[
        "goerr"
    ],
    zip_safe=False
)
