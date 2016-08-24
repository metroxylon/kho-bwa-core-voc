from setuptools import setup

setup(
    name='heatmap_dendrogram',
    version='0.0.1',
    py_modules=['heatmap_dendrogram'],
    install_requires=[
        'pandas',
        'numpy',
        'seaborn',
        'matplotlib',
        'scipy',
        'click',
    ],
    entry_points='''
        [console_scripts]
        heatmap_dendrogram=heatmap_dendrogram:cli
    ''',
)
