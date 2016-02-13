# interface to subversion repository

import os, subprocess, tempfile, sys
from lxml import etree
from bl.dict import Dict
from bl.url import URL

class SVN(Dict):
    "direct interface to a Subversion repository using svn and svnmucc via subprocess"

    def __init__(self, url=None, local=None,
            username=None, password=None, 
            svn=None, svnmucc=None, svnlook=None,
            trust_server_cert=True, log=print):
        Dict.__init__(self, url=URL(url or ''), local=local,
            username=username, password=password, 
            svn=svn or 'svn', svnmucc=svnmucc or 'svnmucc', svnlook=svnlook or 'svnlook',
            trust_server_cert=trust_server_cert, log=print)

    def __repr__(self):
        return "SVN(url='%s')" % self.url

    def __call__(self, *args):
        "uses svn to access the repository"
        result = self._subprocess(self.svn, *args)
        if '--xml' in args:
            return etree.XML(result)
        else:
            return result

    def mucc(self, *args):
        "use svnmucc to access the repository"
        return self._subprocess(self.svnmucc, *args)

    def look(self, *args):
        "use svnlook to access the repository"
        return self._subprocess(self.svnlook, *args)

    def _subprocess(self, cmd, *args):
        """uses subprocess.check_output to get and return the output of svn or svnmucc,
        or raise an error if the cmd raises an error.
        """
        stderr = tempfile.NamedTemporaryFile()
        cmdlist = []
        if 'svnlook' not in cmd:
            cmdlist += [cmd, '--non-interactive']
            if self.trust_server_cert==True and 'svnmucc' not in cmd:
                cmdlist += ['--trust-server-cert']
            if self.username is not None:
                cmdlist += ['--username', self.username]
            if self.password is not None:
                cmdlist += ['--password', self.password]
        cmdlist += list(args)
        cmdlist = list(cmdlist)
        try:
            res = subprocess.check_output(cmdlist, stderr=stderr)
        except subprocess.CalledProcessError as e:
            f = open(stderr.name, 'r+b')
            output = f.read(); f.close()
            raise RuntimeError(str(output, 'utf-8')
                ).with_traceback(sys.exc_info()[2]) from None
        return res

    # == USER API COMMANDS == 

    def cat(self, url, rev='HEAD'):
        if self.local not in [None, '']:
            # fast: svnlook cat
            path = os.path.relpath(url, str(self.url))
            return self.look('cat', '--revision', rev, self.local, path)
        else:
            # slow: svn cat
            args = ['--revision', rev, URL(url).quoted()]
            return self('cat', *args)

    def copy(self, src_url, dest_url, msg='', rev='HEAD'):
        args = ['--revision', rev, '--message', msg, 
                URL(src_url).quoted(), URL(dest_url).quoted()]
        return self('copy', *args)

    def delete(self, *urls, msg='', force=False):
        args = ['--message', msg]
        if force==True:
            args.append('--force')
        args += [URL(u).quoted() for u in list(urls)]
        return self('delete', *args)

    def diff(self, *args):
        return self('diff', *args)

    def export(self, src_url, dest_path, rev='HEAD', depth='infinity', pegrev=None):
        if pegrev is not None:
            src_url += '@'+pegrev
        args = ['--revision', rev, '--depth', depth, 
                URL(src_url).quoted(), dest_path]
        return self('export', *args)

    def filesize(self, url, rev='HEAD'):
        if self.local not in [None, '']:
            # fast: svnlook filesize
            path = os.path.relpath(url, str(self.url))
            return self.look('filesize', '--revision', rev, self.local, path)
        else:
            # slow: svn cat
            return len(self.cat(url, rev=rev))

    def importe(self, src_path, dest_url, msg='', depth='infinity', force=False):
        args = ['--message', msg, '--depth', depth]
        if force==True: args.append('--force')
        args += [src_path, URL(dest_url).quoted()]
        return self('import', *args)

    def info(self, url, rev='HEAD', depth='empty', verbose=True, xml=True):
        args = ['--revision', rev, '--depth', depth]
        if xml==True: args.append('--xml')
        if verbose==True and xml!=True: 
            args.append('--verbose')
        args.append(URL(url).quoted())
        return self('info', *args)

    def list(self, url, rev='HEAD', depth='infinity',
                verbose=True, xml=True):
        args = ['--revision', rev, '--depth', depth]
        if xml==True: 
            args.append('--xml')
        if verbose==True and xml != True: 
            args.append('--verbose')
        args.append(URL(url).quoted())
        return self('list', *args)

    def lock(self, *urls, msg='', force=False): 
        args = ['--message', msg]
        if force==True: 
            args.append('--force')
        args += [URL(u).quoted() for u in list(urls)]
        self('lock', *args)

    def log(self, url, revs='HEAD:1', verbose=True, xml=True):
        args = ['--revision', revs]
        if verbose==True: args.append('--verbose')
        if xml==True: args.append('--xml')
        args.append(URL(url).quoted())
        return self('log', *args)

    def mkdir(self, url, msg='', parents=True):
        args = ['--message', msg]
        if parents==True: 
            args.append('--parents')
        args.append(URL(url).quoted())
        return self('mkdir', *args)

    def move(self, src_url, dest_url, msg='',
            rev='HEAD', force=False):
        args = ['--revision', rev, '--message', msg]
        if force==True: 
            args.append('--force')
        args += [URL(src_url).quoted(), URL(dest_url).quoted()]
        return self('move', *args)

    def put(self, path, dest_url, msg=''):
        args = ['--message', msg, path, URL(dest_url).quoted()]
        return self.mucc('put', *args)

    def remove(self, *urls, msg='', force=False):
        args = ['--message', msg]
        if force==True: 
            args.append('--force')
        args += [URL(u).quoted() for u in list(urls)]
        return self('remove', *args)

    def unlock(self, *urls, force=False):
        args = []
        if force==True: 
            args.append('--force')
        args += [URL(u).quoted() for u in list(urls)]
        return self('unlock', *args)

    # == Properties == 

    def proplist(self, url, rev='HEAD', depth='infinity', 
            xml=True, verbose=True, inherited=True, changelist=None):
        args = ['--revision', rev, '--depth', depth]
        if xml==True: args += ['--xml']
        if verbose==True: args += ['--verbose']
        if inherited==True: args += ['--show-inherited-props']
        if changelist is not None: args += ['--changelist', changelist]
        args += [URL(url).quoted()]
        return self('proplist', *args)

    def propget(self, name, url, rev='HEAD', depth='infinity', xml=True):
        pass

    def propset(self, name, url, rev='HEAD', msg='', 
                depth='infinity', force=False):
        pass

    def propdel(self, name, url, rev=None, 
                depth='infinity'):
        pass

    def propedit(self, name, url, rev=None, msg='', 
                force=False):
        pass

if __name__ == '__main__':
    import doctest
    doctest.testmod()
