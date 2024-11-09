from setuptools import setup, find_packages

setup(
    name='sparc-cli',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'streamlit>=1.24.0',
        'pytest>=7.0.0',
        'aider-chat>=0.8.0',
        'rich>=10.0.0',
        'gitpython>=3.1.0',
    ],
    entry_points={
        'console_scripts': [
            'sparc-cli=sparc_cli:main',
        ],
    },
)
