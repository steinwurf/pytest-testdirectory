import os

def test_self(testdirectory):

    r = testdirectory.run('python', '-m', 'pip', 'list')

    #whl = testdirectory.copy_file('dist/*.whl')
    #r = testdirectory.run('python', '-m', 'pip', 'install', whl)
    print(r)

    r = testdirectory.run('python', '-m', 'pip', '--version')

    print(r)
    assert 0
    testdirectory.run('python', '-m', 'pytest', '--version')
