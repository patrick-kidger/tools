import subprocess


def shell(cmd, **kwargs):
    """Runs the given :cmd: in the shell and returns its stdout as a string. Additional :kwargs: are passed to the call
    to subprocess.run.
    """
    return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, **kwargs).stdout.decode('utf-8')
