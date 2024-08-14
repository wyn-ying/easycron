from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyeasycron',
    version='0.1.2',
    url='https://github.com/wyn-ying/pyeasycron',
    author='wyn-ying',
    author_email='yingwen.wyn@gmail.com',
    description='An easy way to make function run as cron',
    keywords=['easycron', 'cron', 'cronjob', 'schedule', 'automation'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=('docs', 'test', 'test.*')),
    install_requires=[
        'croniter'
    ],
    classifiers=[
        'Programming Language :: Python',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12'
    ],
)
