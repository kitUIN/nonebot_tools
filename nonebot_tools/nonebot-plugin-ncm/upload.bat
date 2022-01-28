cd C:\Users\kulujun\PycharmProjects\nonebot_tools\nonebot_tools\nonebot-plugin-ncm
python.exe setup.py bdist_wheel
python.exe -m twine upload dist/*
pip install nonebot-plugin-ncm --upgrade
rd /s /q nonebot_plugin_ncm.egg-info
rd /s /q build
rd /s /q dist
