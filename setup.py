from distutils.core import setup

from model_attachments import VERSION

setup(
    name='django-model-attachments',
    version=VERSION,
    description="Django attachments used with m2m relation",
    author='Vittorio Zamboni',
    author_email='vittorio.zamboni@gmail.com',
    license='MIT',
    url='https://github.com/vittoriozamboni/django-model-attachments.git',
    packages=[
        'model_attachments',
    ],
    dependency_links=[
    ],
    install_requires=[
        'django>=1.9',
        'django-braces>=1.8',
    ],
)
