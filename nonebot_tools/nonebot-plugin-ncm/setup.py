import setuptools
requirements = [
    requirement.strip() for requirement in open('requirements.txt', 'r', encoding='utf-8').readlines()
]

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="nonebot-plugin-ncm",
    version="0.1.6",
    author="kitUIN",
    author_email="kulujun@gmail.com",
    description="An ncm music downloader plugin for nonebot2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kitUIN/nonebot_tools/src/nonebot-plugin-ncm",
    packages=setuptools.find_packages(),
    license="MIT License",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
    ], install_requires=requirements,
    python_requires='>=3.7',
)
