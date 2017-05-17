import os

def _test_self(testdirectory):
    whl = testdirectory.copy_file('dist/*.whl')
    testdirectory.run('python', '-m', 'pip', 'install', whl)
    testdirectory.run('python', '-m', 'pytest', '--version')
