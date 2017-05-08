import os

def test_testdirectory(testdirectory):
    """ Unit test for the testdirectory fixture"""
    assert os.path.exists(testdirectory.path())

    sub1 = testdirectory.mkdir('sub1')
    assert os.path.exists(sub1.path())

    sub1.write_binary('ok.txt', b'hello_world')

    ok_path = os.path.join(sub1.path(), 'ok.txt')

    assert os.path.isfile(ok_path)
    sub1.rmfile('ok.txt')
    assert not os.path.isfile(ok_path)

    sub1.write_text('ok2.txt', u'hello_world2', encoding='utf-8')

    ok_path = os.path.join(sub1.path(), 'ok2.txt')

    assert os.path.isfile(ok_path)

    sub2 = testdirectory.mkdir('sub2')
    sub1_copy = sub2.copy_dir(sub1.path())

    assert os.path.exists(os.path.join(sub2.path(), 'sub1'))
    assert os.path.exists(sub1_copy.path())

    # Run a command that should be available on all platforms
    r = sub1.run('python', '--version')

    assert r.returncode == 0
    assert r.stdout.match('Python *') or r.stderr.match('Python *')

    sub3 = testdirectory.mkdir('sub3')
    ok3_file = sub3.copy_file(ok_path, rename_as='ok3.txt')

    assert testdirectory.contains_dir('sub3')
    assert not testdirectory.contains_dir('notheredir')

    assert os.path.isfile(ok3_file)
    assert sub3.contains_file('ok3.txt')
    assert not sub3.contains_file('noherefile.txt')

    sub3.rmdir()
    assert not testdirectory.contains_dir('sub3')

    sub4 = testdirectory.mkdir('sub4')
    sub4.mkdir('sub5')

    # Will look for 'sub4/sub5'
    assert testdirectory.contains_dir(os.path.join('sub4', 'sub5'))
    assert testdirectory.contains_dir(os.path.join('sub*', 'sub5'))
    assert testdirectory.contains_dir(os.path.join('sub*', 's*5'))

    sub5 = sub4.join('sub5')
    sub5.rmdir()

    assert not testdirectory.contains_dir(os.path.join('sub4', 'sub5'))
