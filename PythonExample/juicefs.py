#!/bin/bash

''':'
PYTHON=`command -v python2`
if [ -z $PYTHON ]; then
    PYTHON=`command -v python`
fi
if [ -z $PYTHON ]; then
    PYTHON=`command -v python3`
fi
if [ -z $PYTHON ]; then
    echo "no Python available, please install it first"
    exit 1
fi
exec $PYTHON $0 $@
exit $?
''' #'''
import sys
import os
import stat
import time
import platform
import optparse
import json
import getpass
import socket
import struct
import signal
import locale
import syslog
import threading
import subprocess
import shutil
import hashlib
import resource
import pwd, grp
import base64

try:
    # python 3+
    import http.client as httplib
    from urllib.parse import urlencode, quote
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
    raw_input = input
except ImportError:
    # python 2.5+
    import httplib
    from urllib import urlencode, quote
    from urllib2 import urlopen, Request, HTTPError

OS = platform.system()
syslog.openlog("juicefs", syslog.LOG_PID | syslog.LOG_USER)
ORIG_ARGV = sys.argv[:]
COMMAND = os.path.abspath(sys.argv[0])
SELFPATH = os.path.realpath(COMMAND)
insideDocker = os.path.exists('/.dockerenv')

def log(level, msg):
    sys.stderr.write(msg + "\n")
    if not insideDocker:
        syslog.syslog(level, msg)

ADDRESS = "d.juicefs.io:10086"
BASE = "http://%s/static" % ADDRESS
JFS_URL = BASE + "/juicefs"
MOUNT_URL = BASE + "/%s/mount" % OS
CFG_URL = os.environ.get("CFG_URL", "https://juicefs.io/volume/%s/mount")

ROOT = os.path.join(os.environ["HOME"] if os.getuid() else "/root", ".juicefs")
MOUNT_PATH = os.path.join(ROOT, "jfsmount")

def is_updated(path, url):
    if not os.path.exists(path):
        return True
    if os.path.getmtime(path)+60 > time.time():
        return False
    try:
        mtime = time.gmtime(os.path.getmtime(path))
        conn = httplib.HTTPConnection(ADDRESS)
        conn.request("HEAD", url)
        res = conn.getresponse()
        last_mod = time.strptime(res.getheader("last-modified"), "%a, %d %b %Y %H:%M:%S %Z")
        return last_mod > mtime
    except HTTPError:
        return False

def download(path, url):
    if not os.path.exists(os.path.dirname(path)):
        os.mkdir(os.path.dirname(path))
    if is_updated(path, url):
        req = Request(url)
        req.add_header('Accept-encoding', 'gzip')
        req.add_header('User-Agent', 'JuiceFS')
        data = urlopen(req).read()
        tmp = path + ".tmp"
        f = open(tmp, 'wb')
        f.write(data)
        f.close()
        os.chmod(tmp, stat.S_IXUSR | stat.S_IRUSR | stat.S_IROTH | stat.S_IXOTH)
        if os.path.exists(path):
            os.remove(path)
        os.rename(tmp, path)

if 'JFSCHAN' in os.environ:
    MOUNT_URL += "." + os.environ['JFSCHAN']
    MOUNT_PATH += "." + os.environ['JFSCHAN']

def install(cfg):
    try:
        download(MOUNT_PATH, MOUNT_URL)
    except Exception:
        if not os.path.exists(MOUNT_PATH):
            log(syslog.LOG_ERR,"Failed to download jfsmount: %s" % sys.exc_info()[1])
            sys.exit(1)
    if platform.system() == "Linux" and not insideDocker:
        subprocess.call("modprobe fuse", shell=True, stdout=subprocess.PIPE)

def gen_s3_endpoint(region, bucket, external):
    # this endpoint is fake
    return "%s.s3-%s.amazonaws.com" % (bucket, region)

def gen_oss_endpoint(region, bucket, external):
    if external:
        return "%s.oss-%s.aliyuncs.com" % (bucket, region)
    host = "%s.oss-%s-internal.aliyuncs.com" % (bucket, region)
    if test_endpoint(host):
        return host
    return "%s.vpc100-oss-%s.aliyuncs.com" % (bucket, region)

def gen_ufile_endpoint(region, bucket, external):
    # https://docs.ucloud.cn/storage_cdn/ufile/faq.html
    if external:
        return '%s.%s.ufileos.com' % (bucket, region)
    if region == 'cn-bj':
        # TODO: choose the best endpoint for a zone
        return '%s.ufile.cn-north-02.ucloud.cn' % bucket
    elif region == 'cn-gd':
        return bucket + '.internal-cn-gd-02.ufileos.com'
    else:
        return '%s.internal-%s-01.ufileos.com' % (bucket, region)

def gen_qingstor_endpoint(region, bucket, external):
    return "%s.%s.qingstor.com" % (bucket, region)

def gen_gs_endpoint(region, bucket, external):
    return "%s.%s.googleapis.com" % (bucket, region)

def gen_ks3_endpoint(region, bucket, external):
    if external:
        return "%s.ks3-%s.ksyun.com" % (bucket, region)
    return "%s.ks3-%s-internal.ksyun.com" % (bucket, region)

def gen_qiniu_endpoint(region, bucket, external):
    return "%s.%s-s3.qiniu.com" % (bucket, region)

def gen_cos_endpoint(region, bucket, external):
    return "%s.cos.%s.myqcloud.com" % (bucket, region)

def gen_wasb_endpoint(region, container, external):
    if region.endswith('china'):
        return "%s.core.chinacloudapi.cn" % container
    return "%s.core.windows.net" % container

def gen_nos_endpoint(region, bucket, external):
    if external:
        return '%s.nos-%s.126.net' % (bucket, region)
    return '%s.nos-%s-i.netease.com' % (bucket, region)

def gen_mss_endpoint(region, bucket, external):
    if region == 'northchina1':
        return '%s.mtmss.com' % bucket
    return "%s.%s.mtmss.com" % (bucket, region)

def gen_jss_endpoint(region, bucket, external):
    if external:
        return "%s.oss.%s.jcloudcs.com" % (bucket, region)
    return "%s.oss-internal.%s.jcloudcs.com" % (bucket, region)

def gen_speedy_endpoint(region, bucket, external):
    return "%s.oss-%s.speedycloud.org" % (bucket, region)

def gen_b2_endpoint(region, bucket, external):
    return "%s.backblaze.com" % bucket

def gen_ceph_endpoint(region, bucket, external):
    return bucket

NEED_TESTS = ("oss", "ufile", "ks3", "nos", "jss")

def support_https(storage, endpoint):
    if storage == 'ufile':
        return not ('.internal-' in endpoint or endpoint.endswith('.ucloud.cn'))
    elif storage == 'oss':
        return not ('.vpc100-oss' in endpoint or 'internal.aliyuncs.com' in endpoint)
    elif storage == 'jss':
        return '.oss-internal.' not in endpoint
    else:
        return True

def test_endpoint(host):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(2)
        s.connect((host, 80))
        return True
    except socket.error:
        return False
    finally:
        s.close()

def umount(mp, force=True):
    if OS == "Linux":
        os.system("umount %s %s" % ("-l" if force else "", mp))
    else:
        os.system("diskutil umount %s %s" % ("force" if force else "", mp))

def create_endpoint(name, cfg, options, suffix=''):
    storage = cfg['storage' + suffix]
    bucket = cfg['bucket' + suffix]
    if "." not in bucket:
        region = cfg['region' + suffix]
        endpoint = globals()["gen_%s_endpoint" % storage](region, bucket, getattr(options, "external", False))
        if storage in NEED_TESTS and not getattr(options, "external", False) and not getattr(options, "internal", False) and not test_endpoint(endpoint):
            endpoint = globals()["gen_%s_endpoint" % storage](region, bucket, True)
            # log(syslog.LOG_NOTICE, "use external endpoint: %s" % endpoint)
        cfg['bucket' + suffix] = endpoint
        save_cfg(name, cfg)
    else:
        endpoint = bucket
    if not endpoint.startswith("http"):
        if support_https(storage, endpoint):
            endpoint = "https://" + endpoint
        else:
            endpoint = "http://" + endpoint
    return endpoint

def gen_mapping(ids, salt=''):
    mapping = {}
    names = set(["root"])
    for id, name in sorted(ids):
        if name in names: continue
        names.add(name)
        a, b = struct.unpack("QQ", hashlib.md5((salt + name + salt).encode('utf8')).digest())
        uid = (a ^ b) % (1<<15) + 10000
        while uid in mapping:
            uid += 1
        mapping[uid] = (id, name)
    return ','.join("%s:%s" % (id, uid) for uid, (id, _) in mapping.items())

mount_pid = None
last_active = None

def check_mount_point(mp):
    global last_active
    last_active = time.time()
    while True:
        if last_active+10 < time.time():
            try:
                os.stat(mp)
                last_active = time.time()
            except Exception:
                pass
        time.sleep(10)

def watchdog():
    global last_active
    last_active = time.time()
    while True:
        if last_active+1800 < time.time():
            log(syslog.LOG_NOTICE,"watchdog: kill %d" % mount_pid)
            try: os.kill(mount_pid, signal.SIGKILL)
            except Exception: pass
            last_active = time.time()
        time.sleep(10)

def start_thread(target, args=()):
    t = threading.Thread(target=target, args=args)
    t.daemon = True
    t.start()

def prepare_environ(name, cfg, options):
    host, port = cfg['master'].split(':')
    port = int(port) - 100
    rootname = cfg.get('rootname', name)
    master = "%s:%s:/%s" % (host, port, rootname)
    os.environ["master"] = master
    os.environ['mfspassword'] = cfg['password']
    os.environ['GOGC'] = '50'
    os.environ["UIDS"] = gen_mapping([(p.pw_uid, p.pw_name) for p in pwd.getpwall()], rootname)
    os.environ["GIDS"] = gen_mapping([(p.gr_gid, p.gr_name) for p in grp.getgrall()], rootname)
    os.environ["BLOCK_PARTITIONS"] = str(cfg.get("partitions", 0))
    os.environ["storage"] = cfg["storage"]
    os.environ["endpoint"] = create_endpoint(name, cfg, options)
    os.environ["ACCESS_KEY"] = cfg.get('accesskey') or ''
    os.environ["SECRET_KEY"] = cfg.get('secretkey') or ''
    if cfg.get('replicated', False):
        os.environ["storage2"] = cfg['storage2']
        os.environ["endpoint2"] = create_endpoint(name, cfg, options, "2")
        os.environ["ACCESS_KEY2"] = cfg.get('accesskey2') or ''
        os.environ["SECRET_KEY2"] = cfg.get('secretkey2') or ''

def test_credentials(name, cfg, options):
    if 'tested' in cfg:
        return
    prepare_environ(name, cfg, options)
    args = ["juicefs", "-ssl", "-test"]
    if getattr(options, "debug", False):
        args.append("-v")
    pid = os.fork()
    if pid == 0:
        os.execv(MOUNT_PATH, args)
        sys.exit(0)
    _, status = os.waitpid(pid, 0)
    if status != 0:
        sys.exit(-1)
    cfg['tested'] = 1
    save_cfg(name, cfg)

def gen_opts(name, options):
    opts = "fsname=JuiceFS:%s" % name
    if options.fuse_opts:
        opts += ',' + options.fuse_opts
    if options.allow_other or os.getuid()==0:
        opts += ",allow_other"
    elif options.allow_root:
        opts += ",allow_root"
    if not options.enable_xattr:
        opts += ",mfsnoxattrs"
    if OS == 'Darwin':
        opts += ",allow_recursion"
    elif OS == "Linux":
        opts += ",nonempty"
    return opts

def launch_mount(name, mountpoint, cfg, options):
    prepare_environ(name, cfg, options)
    os.environ['MAX_UPLOAD'] = str(options.maxUploads)
    args = ["juicefs", "-mountpoint", mountpoint, "-ssl",
            "-cacheDir", os.path.join(options.cacheDir, name),
            "-cacheSize", str(options.cacheSize),
            "-o", gen_opts(name, options)]
    if options.debug:
        args.append("-v")
        if options.foreground:
            args.append("-nosyslog")
    if options.writeback:
        args.append("-async")
    if options.gc:
        args.append("-gc")
    if options.dry:
        args.append("-dry")
    if options.nosync:
        args.append("-nosync")
    if options.metacache:
         args.extend(["-metacacheto", "300"])
    if options.cacheGroup:
        args.append("-cacheGroup")
        args.append(options.cacheGroup)
    if options.flip:
        args.append("-flip")
    if options.address:
        args.append("-http")
        args.append(options.address)
    if cfg.get('compatible', False):
        args.append("-direct")

    if not options.foreground and (os.getppid() != 1 or insideDocker) or options.background:
        daemonize(mountpoint, options)

    # increase rlimit
    i = 100000
    while i > 1000:
        try:
            resource.setrlimit(resource.RLIMIT_NOFILE, (i, i))
            break
        except Exception as e:
            i = i * 2 / 3

    global mount_pid
    start_thread(check_mount_point, (mountpoint,))
    start_thread(watchdog)
    start = time.time()
    c = 0
    while True:
        try:
            c += 1
            umount(mountpoint)
            mount_pid = os.fork()
            if mount_pid == 0:
                os.execv(MOUNT_PATH, args)
                return
            _, code = os.waitpid(mount_pid, 0)
            if code == 0:
                return
            if c == 2 and time.time() - start < 10:
                return
            self_upgrade()
        except Exception:
            log(syslog.LOG_CRIT, "mount exited: %s" % sys.exc_info()[1])
            if mount_pid is not None:
                os.kill(mount_pid, signal.SIGKILL)
        except BaseException:
            break
        finally:
            mount_pid = None

def require_input(msg):
    if not sys.stdin.isatty():
        return ''
    return raw_input(msg + ": ")

def save_cfg(name, cfg):
    path = os.path.join(ROOT, name + ".conf")
    jdir = os.path.dirname(path)
    if not os.path.exists(jdir):
        os.makedirs(jdir)
    f = open(path, 'wb')
    f.write(json.dumps(cfg, indent=2).encode('utf-8'))
    f.close()
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)  # only owner can read it

def load_cfg(name, **kw):
    path = os.path.join(ROOT, name + ".conf")
    cfg = {}
    try:
        if os.path.exists(path):
            cfg = json.load(open(path))
    except Exception:
        log(syslog.LOG_CRIT, "Failed to load cached config: %s" % sys.exc_info()[1])
        os.remove(path)
    cfg.update(kw)
    return update_cfg(name, **cfg)

KEYNAMES = {
    "s3": ("Access key ID", "Secret access key"),
    "ufile": ("Public key", "Private key"),
    "oss": ("Access key ID", "Access key secret"),
    "cos": ("Secret ID", "Secret key"),
    "qiniu": ("Access key", "Secret key"),
    "ks3": ("Secret ID", "Secret key"),
    "wasb": ("Storage account", "access key"),
    "ceph": ("cluster", "user"),
    "b2": ("Account ID", "Application Key"),
}

def access_key_name(storage):
    return (KEYNAMES.get(storage) or KEYNAMES["s3"])[0]

def secret_key_name(storage):
    return (KEYNAMES.get(storage) or KEYNAMES["s3"])[1]

def update_cfg(name, token=None, **kw):
    path = os.path.join(ROOT, name + ".conf")
    if not token and 'passwd' in kw:
        token = kw['passwd']
    if not token:
        token = require_input("Token for %s" % name)
    try:
        param = urlencode({'token': token})
        data = urlopen(CFG_URL % name, param.encode('utf-8')).read()
        cfg = kw.copy()
        d = json.loads(data.decode('utf-8'))
        # don't update bucket name
        if 'bucket' in cfg:
            d.pop('bucket')
        cfg.update(d)
    except HTTPError:
        print(("Invalid name or token: %s" % sys.exc_info()[1]))
        cfg = dict(token=token, **kw)
        if 'bucket' not in cfg:
            sys.exit(1)

    storage = cfg['storage']
    bucket = cfg['bucket']
    if storage == 'cos' and '-' not in bucket:
        appid = require_input("AppID for COS")
        if not appid.isdigit():
            print("AppID can only have digits")
            sys.exit(1)
        cfg['bucket'] = "%s-%s" % (bucket,appid)
    if storage == 's3':
        if 'accesskey' not in cfg:
            cfg['accesskey'] = os.environ.get("AWS_ACCESS_KEY_ID")
        if 'secretkey' not in cfg:
            cfg['secretkey'] = os.environ.get("AWS_SECRET_ACCESS_KEY")

    if storage != 'gs':
        if cfg.get('accesskey') is None:
            cfg['accesskey'] = require_input("%s for %s://%s" % (access_key_name(storage), storage, bucket))
        if cfg.get('secretkey') is None:
            cfg['secretkey'] = require_input("%s for %s://%s" % (secret_key_name(storage), storage, bucket))
    if '/' in cfg['accesskey']:
        cfg['accesskey'] = quote(cfg['accesskey'], safe='')

    storage2 = cfg.get("storage2")
    if storage2 == 's3':
        if 'accesskey2' not in cfg:
            cfg['accesskey2'] = os.environ.get("AWS_ACCESS_KEY_ID")
        if 'secretkey2' not in cfg:
            cfg['secretkey2'] = os.environ.get("AWS_SECRET_ACCESS_KEY")

    if cfg.get('replicated') and storage2 != 'gs':
        bucket2 = cfg['bucket2']
        if storage2 == 'cos' and '-' not in bucket2:
            appid = require_input("AppID for COS")
            if not appid.isdigit():
                print("AppID can only have digits")
                sys.exit(1)
            cfg['bucket2'] = "%s-%s" % (bucket2,appid)
        if cfg.get('accesskey2') is None:
            cfg['accesskey2'] = require_input("%s for %s://%s" % (access_key_name(storage2), storage2, cfg['bucket2']))
        if cfg.get('secretkey2') is None:
            cfg['secretkey2'] = require_input("%s for %s://%s" % (secret_key_name(storage2), storage2, cfg['bucket2']))
        if '/' in cfg['accesskey2']:
            cfg['accesskey2'] = quote(cfg['accesskey2'], safe='')

    save_cfg(name, cfg)
    return cfg


def daemonize(mountpoint, options):
    """
    do the UNIX double-fork magic, see Stevens' "Advanced
    Programming in the UNIX Environment" for details (ISBN 0201563177)
    http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
    """
    pid = os.fork()
    if pid > 0:
        # wait for mount to be ready
        os.waitpid(pid, 0)
        p = os.path.join(mountpoint, ".masterinfo")
        c = 0
        while c < 10 and not os.path.exists(p):
            time.sleep(1)
            c += 1
        if not os.path.exists(p):
            log(syslog.LOG_ERR, "mount %s failed, try with -f to see more details" % mountpoint)
            sys.exit(1)
        sys.exit(0)

    # decouple from parent environment
    os.chdir("/")
    os.setsid()
    os.umask(0)

    # do second fork
    pid = os.fork()
    if pid > 0:
        sys.exit(0)

    # redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    si = open("/dev/null", 'r')
    se = open(options.logpath, 'a+')
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(se.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

def auth():
    parser = optparse.OptionParser(prog="juicefs auth NAME",
        description='authorize a filesystem, so you can mount without specifying them again')

    parser.add_option("--password", type=str,
                      help="the password of the filesystem (deprecated, use token)")
    parser.add_option("--bucket", type=str,
                      help="name of the bucket (optional, deprecated)")
    parser.add_option("--token", type=str,
                      help="the token of the filesystem")
    parser.add_option("--accesskey", type=str,
                      help="the access key id of the bucket (optional)")
    parser.add_option("--secretkey", type=str,
                      help="the secret key of the bucket (optional)")
    parser.add_option("--accesskey2", type=str,
                      help="the access key id of secondary bucket (optional)")
    parser.add_option("--secretkey2", type=str,
                      help="the secret key of secondary bucket (optional)")
    options, args = parser.parse_args()
    if not args:
        print("No filesystem specified")
        return 1
    name = args[0]

    if options.password:
        options.token = options.password
    cfg = update_cfg(name,
        token=options.token,
        accesskey=options.accesskey,
        secretkey=options.secretkey,
        accesskey2=options.accesskey2,
        secretkey2=options.secretkey2)
    install(cfg)
    cfg.pop('tested', None)
    test_credentials(name, cfg, options)


def mount():
    parser = optparse.OptionParser(prog="juicefs mount NAME MOUNTPOINT",
                                   description='Mount a filesystem')

    storeOptions = optparse.OptionGroup(parser, "Object Storage Options")
    storeOptions.add_option("--external", action="store_true",
                            help="Use the external endpoint (outside of the region)")
    storeOptions.add_option("--internal", action="store_true",
                            help="use only the internal endpoint (within the same region)")
    storeOptions.add_option("--max-uploads", dest="maxUploads", type=int, default=50,
                            help="Max number of concurrent uploads (default: 50)")
    storeOptions.add_option("--gc", action="store_true",
                            help="cleanup unused chunks after mounting immediately")
    storeOptions.add_option("--dry", action="store_true",
                            help="do not delete chunks during GC")
    storeOptions.add_option("--flip", action="store_true",
                            help="flip the two replicated bucket (prefer secondary bucket)")
    storeOptions.add_option("--no-sync", dest="nosync", action="store_true",
                            help="donot sync the replicated object store")
    parser.add_option_group(storeOptions)

    cacheOptions = optparse.OptionGroup(parser, "Cache Options")
    cacheOptions.add_option("--cache-dir", dest="cacheDir", type=str, default="/var/jfsCache",
                      help="A local directory to cache data (default: /var/jfsCache)")
    cacheOptions.add_option("--cache-size", dest="cacheSize", type=int, default=1024,
                      help="the limit of cache in MB (default: 1G)")
    cacheOptions.add_option("--cache-group", dest="cacheGroup", type=str, default="",
                      help="the name of group to share local cache (default: no sharing)")
    cacheOptions.add_option("--writeback", action="store_true",
                      help="write small files (<4M) in local disk first and upload to object store in background")
    cacheOptions.add_option("--metacache", action="store_true",
                       help="cache directories in client")
    parser.add_option_group(cacheOptions)

    fuseOptions = optparse.OptionGroup(parser, "FUSE Options")
    fuseOptions.add_option("--allow-other", dest="allow_other", action="store_true",
                           help="allow other users to access (enabled when mounted as root)")
    fuseOptions.add_option("--allow-root", dest="allow_root", action="store_true",
                           help="allow root to access")
    fuseOptions.add_option("--enable-xattr", dest="enable_xattr", action="store_true",
                           help="Enable xattr support")
    fuseOptions.add_option("-o", dest="fuse_opts", type=str,
                           help="other fuse options")
    parser.add_option_group(fuseOptions)

    parser.add_option("-f", dest="foreground", action="store_true",
                      help="run in foreground")
    parser.add_option("-b", dest="background", action="store_true",
                      help="run in background in Docker")
    parser.add_option("--http", dest="address", default="",
                      help="listen address to serve files using HTTP (for example, localhost:8080)")
    parser.add_option("--log", dest="logpath", default="/var/log/juicefs.log",
                      help="path of log file (default: /var/log/juicefs.log)")
    parser.add_option("-v", dest="debug", action="store_true",
                      help="enable debug logging")
    # parser.add_argument("--autoUpdate", action="store_true",
    #                     help="auto update")

    deprecated = optparse.OptionGroup(parser, "Deprecated Options")
    deprecated.add_option("--async", dest="writeback", action="store_true",
                          help="see --writeback")
    deprecated.add_option("--ssl", action="store_true",
                          help="Use HTTPS to access object store (always enabled)")
    deprecated.add_option("--dircache", dest="metacache", action="store_true",
                          help="see --metacache")
    deprecated.add_option("-d", dest="debug", action="store_true",
                          help="see -v")
    deprecated.add_option("--cacheDir", type=str, default="/var/jfsCache",
                          help="see --cache-dir")
    deprecated.add_option("--cacheSize", type=int, default=1024,
                          help="see --cache-size")
    parser.add_option_group(deprecated)

    if sys.argv[0].endswith("mount.juicefs"):
        # called via mount or fstab
        args, others = sys.argv[:3], sys.argv[3:]
        # remove the leading '/' added by systemd
        if args[1].startswith("/"):
            args[1] = args[1][1:]
        fuse_opts = []
        BAD_OPTS = ('_netdev', 'rw', 'defaults')
        for i in range(len(others)):
            if others[i] == "-o":
                opts = others[i + 1].split(',')
                for opt in opts:
                    opt = opt.strip()
                    if not opt or opt in BAD_OPTS: continue
                    if '=' in opt and parser.has_option("--"+opt.split('=')[0].strip()):
                        k, v = opt.split('=')
                        args += ['--' + k.strip(), v.strip()]
                    elif parser.has_option("--"+opt) and parser.get_option("--"+opt).action == "store_true":
                        args += ['--' + opt]
                    else:
                        fuse_opts.append(opt)
        if fuse_opts:
            args += ['-o', ','.join(fuse_opts)]
        sys.argv = args

    options, args = parser.parse_args()
    if len(args) < 2:
        print("No filesystem and mountpoint specified")
        return 1
    name, mountpoint = args

    # call-out from Kubernetes/Flexvolume
    kw = {}
    if mountpoint.startswith("{") and mountpoint.endswith("}"):
        jopt = json.loads(mountpoint)
        mountpoint = name
        name = jopt.get('name', jopt.get('kubernetes.io/pvOrVolumeName'))
        if not name:
            _fail("no name provided")
        for k in ('token', 'accesskey', 'secretkey'):
            if k in jopt:
                kw[k] = jopt[k]
            else:
                sk = 'kubernetes.io/secret/' + k
                if sk in jopt:
                    kw[k] = base64.standard_b64decode(jopt[sk]).decode('utf8')
        options.__dict__.update(jopt)

    if not os.path.exists(mountpoint):
        try:
            os.makedirs(mountpoint)
        except OSError:
            umount(mountpoint)
    try:
        if os.listdir(mountpoint):
            log(syslog.LOG_WARNING, "%s is not empty" % mountpoint)
    except Exception:
        umount(mountpoint)

    if os.getuid() != 0:
        if OS == 'Darwin':
            if os.stat(mountpoint).st_uid != os.getuid():
                log(syslog.LOG_ERR, "current user should own %s" % mountpoint)
                sys.exit(1)
        else:
            try:
                t = os.path.join(mountpoint, "test")
                f = open(t, 'w')
                f.close()
                os.remove(t)
            except IOError:
                log(syslog.LOG_ERR, "Do not have write permission on %s" % mountpoint)
                sys.exit(1)


    if not os.path.exists(options.cacheDir):
        os.makedirs(options.cacheDir)

    cfg = load_cfg(name, **kw)
    install(cfg)
    test_credentials(name, cfg, options)
    launch_mount(name, mountpoint, cfg, options)


def find_master_addr(path):
    path = os.path.abspath(path)
    d = path if os.path.isdir(path) else os.path.dirname(path)
    while d != '/' and not os.path.exists(os.path.join(d, ".masterinfo")):
        d = os.path.dirname(d)
    if d == '/': return
    f = open(os.path.join(d, ".masterinfo"), 'rb')
    masterinfo = f.read()
    f.close()
    port, = struct.unpack(">H", masterinfo[4:6])
    addr = ("127.0.0.1", port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.setblocking(1)
    return sock

def info():
    parser = optparse.OptionParser(prog="juicefs info [PATH]",
        description="""Show information of a directory or file in JuiceFS""")
    parser.add_option("-n", "--plain", action="store_true",
                      help="show numbers in plain format")
    options, paths = parser.parse_args()
    if not paths:
        parser.print_usage()
        return

    conn = find_master_addr(paths[0])
    if not conn:
        print(('%s is not inside JuiceFS' % paths[0]))
        return 1
    CLTOMA_FUSE_READ_CHUNK = 432
    CLTOMA_FUSE_GETDIRSTATS = 462

    def snum(n):
        locale.setlocale(locale.LC_NUMERIC, 'en_US.UTF-8')
        return locale.format("%d", n, grouping=True)

    def ssize(s):
        if options.plain or s < 1024:
            return str(s)
        b = 0
        while s > 1024:
            s /= 1024.0
            b += 1
        return "%.2f%s" % (s, 'BKMGTPE'[b] if b > 0 else '')

    for path in paths:
        print((path + ":"))
        stat = os.stat(path)
        if os.path.isdir(path):
            conn.sendall(struct.pack("!IIII", CLTOMA_FUSE_GETDIRSTATS, 8, 1, stat.st_ino))
            rcmd, size = struct.unpack("!II", conn.recv(8))
            if size == 60:
                inodes, dirs, files, _, _, chunks, _, _, length, size, _ = \
                    struct.unpack("!IIIIIIIIQQQ", conn.recv(60)[4:])
            elif size == 36:
                inodes, dirs, files, chunks, length, size = struct.unpack("!IIIIQQ", conn.recv(36)[4:])
            print((" inodes: \t%s" % snum(inodes)))
            print(("  directories: \t%s" % snum(dirs)))
            print(("  files: \t%s" % snum(files)))
            print((" chunks: \t%s" % snum(chunks)))
            print((" length: \t%s" % ssize(length)))
            print((" size: \t\t%s" % ssize(size)))
        else:
            print((' inode: \t%s' % stat.st_ino))
            print((' length: \t%s' % ssize(stat.st_size)))
            print((' size: \t\t%s' % ssize((((stat.st_size - 1) >> 18) + 1) << 18)))
            chunks = ((stat.st_size-1) >> 26) + 1
            print((" chunks: \t%s" % chunks))
            for i in range(chunks):
                conn.sendall(struct.pack("!IIIIIB", CLTOMA_FUSE_READ_CHUNK, 13, 1, stat.st_ino, i, 0))
                cmd, size = struct.unpack("!II", conn.recv(8))
                data = conn.recv(size)
                if len(data) == 24:
                    _, chunkid, clength = struct.unpack("!QQI", data[4:])
                    print(("% 5d:\t%s\t%s" % (i, chunkid, ssize(clength))))
                else:
                    flag = data[12]
                    if flag == '\0':
                        clength, = struct.unpack("!Q", data[4:12])
                        print(("% 5d:\t%s\t%s") % (i, data[24:], ssize(clength)))
                        break
                    elif flag == '\2':
                        clength, = struct.unpack("!Q", data[4:12])
                        print(("% 5d:\t%s\t%s") % (i, data[17:], ssize(clength)))
                        break
                    else:
                        n = int((len(data) - 13)/20)
                        for j in range(n):
                            cid,clen,off,l = struct.unpack("!QIII",data[13+j*20:13+j*20+20])
                            print("% 5d:\t%d\t%s\t%s\t%s" % (i, cid, clen, off,(l)))

def heal():
    parser = optparse.OptionParser(prog="juicefs heal NAME",
        description="""Heal a replicated filesystem by sychronize the underlying object storages""")
    parser.add_option("--start", default="",
                      help="start of keys to sync")
    parser.add_option("-v", dest="debug", action="store_true",
                      help="enable debug logging")
    options, args = parser.parse_args()
    if not args:
        parser.print_usage()
        return
    name = args[0]
    cfg = load_cfg(name)
    if not cfg.get('replicated', False):
        print("Only replicated filesystem need heal")
        return 1
    install(cfg)
    prepare_environ(name, cfg, options)
    args = ["juicefs", "-heal", "-ssl"]
    if options.debug:
        args.append("-v")
    if options.start:
        args.extend(["-healStart", options.start])
    os.execv(MOUNT_PATH, args)

def find_name(dst):
    dst = os.path.abspath(dst)
    if OS != 'Linux':
        print("Please specify the NAME of JuiceFS using --name")
        sys.exit(1)
    best_name = None
    common_prefix = ''
    for line in open('/proc/mounts'):
        name, mountpoint, _ = line.split(' ', 2)
        if name.startswith("JuiceFS:") and dst.startswith(mountpoint):
            if not best_name or len(mountpoint) > len(common_prefix):
                best_name = name.split(':')[1]
                common_prefix = mountpoint
    if not best_name:
        print("Please specify the NAME of JuiceFS using --name")
        sys.exit(1)
    return best_name

def import_():
    parser = optparse.OptionParser(prog="juicefs import URI DST",
        description="""Import existing files from object storage, URI should be
        BUCKET_NAME[.DOMAIN]/PREFIX, DST is a directory (part of mounted JuiceFS) """)
    # parser.add_option("--start", default="", help="start of keys to import")
    parser.add_option("--name", default="", help="the name of JuiceFS (optional under Linux)")
    parser.add_option("--mode", default="0440", type=str,
                      help="the Unix permission mode of imported files")
    parser.add_option("-v", dest="debug", action="store_true",
                      help="enable debug logging")
    options, args = parser.parse_args()
    if len(args) < 2:
        parser.print_usage()
        return
    uri, dst = args
    if not os.path.exists(dst):
        os.makedirs(dst)
    dst = os.path.abspath(dst)
    name = options.name or find_name(dst)
    cfg = load_cfg(name)
    install(cfg)
    prepare_environ(name, cfg, options)
    default_endpoint = create_endpoint(name, cfg, options)
    if uri.startswith("/"):
        uri = default_endpoint + uri

    args = ["juicefs", "-import", uri, "-dst", dst, "-mode", options.mode, "-ssl"]
    if options.debug:
        args.append("-v")
    os.execv(MOUNT_PATH, args)


def rmr():
    parser = optparse.OptionParser(prog="juicefs rmr dir",
        description="Fastest way to remove a directory recursively.")
    _, args = parser.parse_args()
    if not args:
        parser.print_usage()
        return

    path = args[0]
    while path.endswith(os.path.sep):
        path = path[:-1]
    path = os.path.abspath(path)
    if not os.path.exists(path):
        print(("%s does not exist." % path))
        return 1

    name = os.path.basename(path).encode('utf-8')
    dirname = os.path.dirname(path).encode('utf-8')
    parent = os.stat(dirname).st_ino
    conn = find_master_addr(dirname)
    if not conn:
        print(('%s is not inside JuiceFS' % args[0]))
        return 1

    CLTOMA_FUSE_UNLINKDIR = 538
    size = 17 + len(name)
    arguments = [CLTOMA_FUSE_UNLINKDIR, size, 0x2E, parent, len(name), name, os.getuid(), os.getgid()]
    req = struct.pack("!IIIIB%dsII" % len(name), *arguments)
    conn.sendall(req)

    data = conn.recv(21)
    if len(data) != 21:
        print("remove %s failed" % args[0])
        return 1
    rcmd, size, msgid, status, success, left = struct.unpack("!IIIBII", data)
    if status != 0:
        if status == 1:
            print("Operation not permitted")
        elif status == 4:
            print("Permission denied")
        else:
            print("failed: %d" % status)
        return 1
    print("%d deleted, %d left." % (success, left))

def snapshot():
    parser = optparse.OptionParser(prog="juicefs snapshot src dst [options]\n    or juicefs snapshot -d path",
        description="""Create or remove snapshot.""")
    parser.add_option("-d", "--delete", action="store_true",
                      help="remove a snapshot")
    parser.add_option("-f", "--force", action="store_true",
                      help="overwrite existing objects, or remove as much as possible")
    parser.add_option("-c", "--copy", action="store_true",
                      help="create objects with current uid,gid,umask (like 'cp')")
    # parser.add_option("-p", "--preserve", action="store_true",
    #                   help="preserve hardlinks")
    options, paths = parser.parse_args()
    if not paths or options.delete and len(paths) != 1 or not options.delete and len(paths) != 2:
        parser.print_usage()
        return

    if options.delete:
        src, dst = "", paths[0]
        inode_src = 0
        while dst.endswith(os.path.sep):
            dst = dst[:-1]
        if not os.path.exists(dst):
            print(("%s does not exist." % dst))
            return 1
    else:
        src, dst = paths
        while src.endswith(os.path.sep):
            src = src[:-1]
        if not os.path.exists(src):
            print(("%s does not exist." % src))
            return 1
        inode_src = os.stat(src).st_ino
        if dst.endswith(os.path.sep):
            dst = os.path.join(dst, os.path.basename(src))
        if not options.force and os.path.exists(dst):
            print(("%s already exists" % dst))
            return 1

    parent = os.path.dirname(os.path.abspath(dst))
    name_dst = os.path.basename(dst).encode('utf-8')
    if not os.path.exists(parent):
        print(("%s does not exists." % parent))
        return 1
    inode_dst = os.stat(parent).st_ino

    conn = find_master_addr(dst)
    if not conn:
        print(('%s is not inside JuiceFS' % dst))
        return 1

    smode = 0
    if options.delete:
        smode |= 0x80
    if options.force:
        smode |= 5
    if options.copy:
        smode |= 2
        umask = os.umask(0)
        os.umask(umask)
    else:
        umask = 0
    # if options.preserve:
    #     smode |= 8

    CLTOMA_FUSE_SNAPSHOT = 468
    MATOCL_FUSE_SNAPSHOT = 469
    req = struct.pack("!IIIIIB%dsIIBH"%len(name_dst), CLTOMA_FUSE_SNAPSHOT, 24+len(name_dst),
        1, inode_src, inode_dst, len(name_dst), name_dst, os.getuid(), os.getgid(), smode, umask)
    conn.sendall(req)
    data = conn.recv(13)
    rcmd, size, msgid, status = struct.unpack("!IIIB", data)
    if status != 0:
        if status == 1:
            print("Operation not permitted")
        elif status == 4:
            print("Permission denied")
        elif status == 34:
            print("Quota exceeded")
        else:
            print("failed: %d" % status)

def merge():
    parser = optparse.OptionParser(prog="juicefs merge SRC ...",
        description="""merge files together without copying.""")
    parser.add_option("-o", "--output", type=str,
                      help="path for merged file")
    parser.add_option("-w", "--overwrite", action="store_true",
                      help="overwrite existing file")
    parser.add_option("-a", "--append", action="store_true",
                      help="append to end of existing file")
    options, srcs = parser.parse_args()
    if not srcs:
        parser.print_usage()
        sys.exit(0)
    dst = options.output
    if not dst:
        print("no output")
        sys.exit(1)
    if os.path.exists(dst):
        if not options.overwrite and not options.append:
            print("%s already exists" % dst)
            sys.exit(1)
        if options.overwrite:
            os.remove(dst)
    if not os.path.exists(dst):
        f = open(dst, 'wb')
        f.close()

    conn = find_master_addr(dst)
    if not conn:
        print(('%s is not inside JuiceFS' % dst))
        return 1

    chunks = []
    CLTOMA_FUSE_READ_CHUNK = 432
    for p in srcs:
        p = os.path.realpath(p)
        if not os.path.isfile(p):
            print("%s is not a file" % p)
            return 1
        st = os.stat(p)
        ino = st.st_ino
        nchunks = ((st.st_size-1) >> 26) + 1
        for i in range(nchunks):
            conn.sendall(struct.pack("!IIIIIB", CLTOMA_FUSE_READ_CHUNK, 13, 1, st.st_ino, i, 0))
            cmd, size = struct.unpack("!II", conn.recv(8))
            data = conn.recv(size)
            flag = data[12]
            if flag == '\2':
                print("Can not merge imported file: %s" % p)
                sys.exit(1)
            chunks.append(data[13:])

    data = b''.join(chunks)
    ino = os.stat(dst).st_ino
    CLTOMA_FUSE_APPEND = 440
    conn.sendall(struct.pack("!IIIII", CLTOMA_FUSE_APPEND, 12+len(data), 1, ino, int(len(data)/20)))
    conn.sendall(data)
    cmd, size = struct.unpack("!II", conn.recv(8))
    data = conn.recv(size)
    if cmd != 441 or size != 5:
        print("invalid response: cmd=%d size=%d" % (cmd, size))
        return 1
    status, = struct.unpack("!B", data[4:])
    if status != 0:
        print("merge failed: code=%d" % status)
        return 1


def init():
    print(json.dumps(dict(status='Success', capabilities=dict(attach=False))))

def _ismounted(mntpath):
    if not os.path.exists(mntpath):
        return False
    return os.path.exists(os.path.join(mntpath, ".masterinfo"))

def _success():
    print(json.dumps(dict(status='Success')))
    sys.exit(0)

def _fail(message='Failed'):
    print(json.dumps(dict(status='Failure', message=message)))
    sys.exit(1)

def unmount():
    mntpath = sys.argv[1]
    if not _ismounted(mntpath):
        _success()
    os.system("umount %s &> /dev/null" % mntpath)
    if _ismounted(mntpath):
        os.system("umount -l %s &> /dev/null" % mntpath)
        # TODO: find the process and kill it
    if _ismounted(mntpath):
        _fail("Failed to umount JuiceFS at %s" % mntpath)
    else:
        _success()

def version():
    download(MOUNT_PATH, MOUNT_URL)
    os.system("%s -V" % MOUNT_PATH)

def usage():
    print("""juicefs COMMAND [options]

COMMAND could be:
  auth      authorize a filesystem
  mount     mount a filesystem
  info      show information of file or directory
  import    import files from existing object storage
  rmr       remove all files/directories recursively
  snapshot  create or remove snapshots
  version   show the version""")


def main():
    if len(sys.argv) < 2:
        return usage()

    if sys.argv[0].endswith("mount.juicefs"):
        command = "mount"
    else:
        sys.argv.pop(0)
        command = sys.argv[0]
    if command == 'import':
        command = 'import_'
    if command not in globals():
        log(syslog.LOG_CRIT, "invalid command: %s" % command)
        usage()
        return 1
    return globals()[command]()

def self_upgrade():
    if is_updated(SELFPATH, JFS_URL):
        try:
            download(SELFPATH, JFS_URL)
            os.execv(COMMAND, ORIG_ARGV)
        except Exception:
            log(syslog.LOG_WARNING, "failed to upgrade: %s" % sys.exc_info()[1])

    if OS == "Linux" and os.getuid() == 0:
        mountpath = "/sbin/mount.juicefs"
        if not os.path.exists(mountpath):
            os.system("ln -s %s %s" % (SELFPATH, mountpath))

if __name__ == '__main__':
    try: self_upgrade()
    except Exception: pass
    sys.exit(main() or 0)
