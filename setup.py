from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='network_scanner_tool',
    version='0.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'network-scanner=network_scanner_tool.cli:main',
        ],
    },
    author='Kiril Ivanov',
    author_email='kiril.ivanov@example.com',
    description='A comprehensive network scanning tool with user authentication, advanced analysis features, and scheduled scans.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/vortex4242/network-scanner-tool',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
