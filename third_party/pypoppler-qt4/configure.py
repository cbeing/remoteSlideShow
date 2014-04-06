import os, sys
import commands
import optparse
import shutil

INSTALL_DIR = ""
BASE_DIR = os.path.dirname(__file__)
SIP_FILE = "poppler-qt4.sip"
BUILD_DIR = "build"
SBF_FILE = "QtPoppler.sbf"


def _cleanup_path(path):
    """
    Cleans the path:
       - Removes traling / or \
    """
    path = path.rstrip('/')
    path = path.rstrip('\\')
    return path


def pkgconfig(package):
    '''
    Calls pkg-config for the given package

    Returns: - None if the package is not found.
             - {'inc_dirs': [List of -L Paths]
                'lib_dirs' : [List of -I Paths]
                'libs ' : [List of -l libs]
               }
    '''
    code, msg = commands.getstatusoutput("pkg-config --exists %s" % package)
    if code != 0:
        return None
    tokens = commands.getoutput("pkg-config --libs --cflags %s" % package).split()
    return {
        'inc_dirs': [ token[2:] for token in tokens if token[:2] == '-I'],
        'lib_dirs': [ token[2:] for token in tokens if token[:2] == '-L'],
        'libs': [ token[2:] for token in tokens if token[:2] == '-l'],
    }

def create_optparser(sipcfg):
    '''Comandline parser'''

    def store_abspath(option, opt_str, value, parser):
        setattr(parser.values, option.dest, os.path.abspath(value))

    def get_default_moddir():
        default = sipcfg.default_mod_dir
        default = os.path.join(default, INSTALL_DIR)
        return default

    p = optparse.OptionParser(usage="%prog [options]")

    default_moddir = get_default_moddir()
    p.add_option("-d", "--destdir", action="callback",
            default=default_moddir, type="string", 
            metavar="DIR",
            dest="moddir", callback=store_abspath, 
            help="Where to install PyPoppler-Qt4 python modules."
            "[default: %default]")
    p.add_option("-s", "--sipdir", action="callback",
            default=os.path.join(sipcfg.default_sip_dir, INSTALL_DIR),
            metavar="DIR", dest="sipdir", callback=store_abspath,
            type="string", help="Where the .sip files will be installed "
            "[default: %default]")

    p.add_option("", "--popplerqt-includes-dir", action="callback",
	    default=None,
            metavar="DIR", dest="popplerqt_inc_dirs", callback=store_abspath,
            type="string", help="PopplerQt include paths"
            "[default: Auto-detected with pkg-config]")
    p.add_option("", "--popplerqt-libs-dir", action="callback",
	    default=None,
            metavar="DIR", dest="popplerqt_lib_dirs", callback=store_abspath,
            type="string", help="PopplerQt libraries paths"
            "[default: Auto-detected with pkg-config]")

    return p

def get_pyqt4_config():
    try:
        import PyQt4.pyqtconfig
        return PyQt4.pyqtconfig.Configuration()
    except ImportError, e:
        print >> sys.stderr, "ERROR: PyQt4 not found."
        sys.exit(1)

def get_sip_config():
    try:
        import sipconfig
        return sipconfig.Configuration()
    except ImportError, e:
        print >> sys.stderr, "ERROR: SIP (sipconfig) not found."
        sys.exit(1)

def get_popplerqt_config(opts):
    config = pkgconfig('poppler-qt4')
    if config is not None:
        found_pkgconfig = True
    else:
        found_pkgconfig = False
        config = {'libs': ['poppler-qt4', 'poppler'],
                  'inc_dirs': None,
                  'lib_dirs': None}

    if opts.popplerqt_inc_dirs is not None:
        config['inc_dirs'] = opts.popplerqt_inc_dirs.split(" ")

    if opts.popplerqt_lib_dirs is not None:
        config['lib_dirs'] = opts.popplerqt_lib_dirs.split(" ")

    
    if config['lib_dirs'] is None or config['inc_dirs'] is None:
        print >> sys.stderr, "ERROR: poppler-qt4 not found."
        print "Try to define PKG_CONFIG_PATH "
        print "or use --popplerqt-libs-dir and --popplerqt-includes-dir options"
        sys.exit(1)

    config['inc_dirs'] = map(_cleanup_path, config['inc_dirs'])
    config['lib_dirs'] = map(_cleanup_path, config['lib_dirs'])
    config['sip_dir'] = _cleanup_path(opts.sipdir)
    config['mod_dir'] = _cleanup_path(opts.moddir)

    print "Using PopplerQt include paths: %s" % config['inc_dirs']
    print "Using PopplerQt libraries paths: %s" % config['lib_dirs']
    print "Configured to install SIP in %s" % config['sip_dir']
    print "Configured to install binaries in %s" % config['mod_dir']

    return config

def create_build_dir():
    dir = os.path.join(BASE_DIR, BUILD_DIR)

    if os.path.exists(dir):
        return

    try:
        os.mkdir(dir)
    except:
        print >> sys.stderr, "ERROR: Unable to create the build directory (%s)" % dir
        sys.exit(1)

def run_sip(pyqtcfg):
    create_build_dir()

    cmd = [pyqtcfg.sip_bin, 
           "-c", os.path.join(BASE_DIR, BUILD_DIR), 
           "-b", os.path.join(BUILD_DIR, SBF_FILE), 
           "-I", pyqtcfg.pyqt_sip_dir, 
           pyqtcfg.pyqt_sip_flags, 
           os.path.join(BASE_DIR, SIP_FILE)]
    os.system( " ".join(cmd) )

def generate_makefiles(pyqtcfg, popplerqtcfg, opts):
    from PyQt4 import pyqtconfig
    import sipconfig

    pypopplerqt4config_file = os.path.join(BASE_DIR, "pypopplerqt4config.py")

    # Creeates the Makefiles objects for the build directory
    makefile_build = pyqtconfig.sipconfig.ModuleMakefile(
        configuration=pyqtcfg,
        build_file=SBF_FILE,
        dir=BUILD_DIR,
        install_dir=popplerqtcfg['mod_dir'],
        warnings=1,
        qt=['QtCore', 'QtGui', 'QtXml']
    )

    # Add extras dependencies for the compiler and the linker
    # Libraries names don't include any platform specific prefixes 
    # or extensions (e.g. the "lib" prefix on UNIX, or the ".dll" extension on Windows)
    makefile_build.extra_lib_dirs = popplerqtcfg['lib_dirs']
    makefile_build.extra_libs = popplerqtcfg['libs']
    makefile_build.extra_include_dirs = popplerqtcfg['inc_dirs']

    # Generates build Makefile
    makefile_build.generate()

 
    # Generates root Makefile

    installs_root = []
    installs_root.append( (os.path.join(BASE_DIR, SIP_FILE), popplerqtcfg['sip_dir']) )
    installs_root.append( (pypopplerqt4config_file, popplerqtcfg['mod_dir']) )
    
    sipconfig.ParentMakefile(
        configuration=pyqtcfg,
        subdirs=[_cleanup_path(BUILD_DIR)],
        installs=installs_root
    ).generate()

def generate_configuration_module(pyqtcfg, popplerqtcfg, opts):
    import sipconfig
    
    content = {
        "pypopplerqt4_sip_dir":    popplerqtcfg['sip_dir'],
        "pypopplerqt4_sip_flags":  pyqtcfg.pyqt_sip_flags,
        "pypopplerqt4_mod_dir":    popplerqtcfg['mod_dir'],
        "pypopplerqt4_modules":    'PopplerQt',
        "popplerqt4_inc_dirs":      popplerqtcfg['inc_dirs'],              
        "popplerqt4_lib_dirs":      popplerqtcfg['lib_dirs'],              
    }

    # This creates the pypopplerqt4config.py module from the pypopplerqt4config.py.in
    # template and the dictionary.
    sipconfig.create_config_module(
        os.path.join(BASE_DIR, "pypopplerqt4config.py"), 
        os.path.join(BASE_DIR, "pypopplerqt4config.py.in"), 
        content)
    

def main():

    sipcfg = get_sip_config()
    pyqtcfg = get_pyqt4_config()

    parser = create_optparser(sipcfg)
    opts, args = parser.parse_args()

    popplerqtcfg = get_popplerqt_config(opts)

    run_sip(pyqtcfg)

    generate_makefiles(pyqtcfg, popplerqtcfg, opts)

    generate_configuration_module(pyqtcfg, popplerqtcfg, opts)

if __name__ == "__main__":
    main()
