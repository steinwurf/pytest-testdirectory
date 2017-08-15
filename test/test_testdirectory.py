import os

def test_run(testdirectory):

    testdirectory.run(['python','--version'])

    testdirectory.run(['python','--version'], stdout=None, stderr=None)

    r = testdirectory.run('python --version')
    assert r.returncode == 0
    assert r.stdout.match('Python *') or r.stderr.match('Python *')

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

def test_write_text(testdirectory):
    ok_path = testdirectory.write_text('ok.txt', u'hello_world',
                                       encoding='utf-8')

    assert testdirectory.contains_file('ok.txt')
    assert os.path.isfile(ok_path)

def test_symlink_file(testdirectory):
    sub1 = testdirectory.mkdir('sub1')
    sub2 = testdirectory.mkdir('sub2')

    ok_path = sub1.write_text('ok.txt', u'hello_world', encoding='utf-8')

    # Create a symlink to 'ok.txt' inside sub2
    link_path = sub2.symlink_file(ok_path)

    assert sub2.contains_file('ok.txt')
    assert os.path.isfile(link_path)

def test_symlink_dir(testdirectory):
    sub1 = testdirectory.mkdir('sub1')
    sub2 = testdirectory.mkdir('sub2')

    # Create a symlink to 'ok.txt' inside sub2
    link_path = sub2.symlink_dir(sub1)

    assert sub2.contains_dir('sub1')
    assert os.path.isdir(link_path)
