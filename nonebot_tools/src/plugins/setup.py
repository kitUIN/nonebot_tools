from setuptools import setup


def get_dis():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()


requirements = [
    requirement.strip() for requirement in open('requirements.txt', 'r', encoding='utf-8').readlines()
]


def main():
    dis = get_dis()
    setup(
        name="nonebot-plugin-ncm",
        version="0.1.0",
        url="https://github.com/kitUIN/nonebot_tools/src/nonebot-plugin-ncm",
        keywords=["nonebot"],
        description="An ncm music downloader plugin for nonebot2",
        long_description_content_type="text/markdown",
        long_description=dis,
        author="kitUIN",
        author_email="kulujun@gmail.com",
        python_requires=">=3.7",
        packages=['nonebot-plugin-ncm'],
        license="MIT License",
        classifiers=[
            "Programming Language :: Python :: 3.7",
            'License :: OSI Approved :: MIT License',
            "Operating System :: OS Independent",
        ], install_requires=requirements,
        include_package_data=True,
    )


if __name__ == '__main__':
    main()
