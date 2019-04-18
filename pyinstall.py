if __name__ == '__main__':
    from PyInstaller.__main__ import run

    opts = ['marker_annotation.py', '-w', '-y']
    # opts = ['marker_annotation.py', '-w', '--icon=shuoGG_re.ico']
    run(opts)
