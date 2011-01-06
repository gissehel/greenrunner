#!/usr/bin/env python
# --------------------------------------------------------------

import socket
import urllib
import urllib2
import cookielib
import os
import hashlib
import time

# from resolvUrl.resolvUrl import ResolvUrl
# from SSLproxy import ConnectHTTPHandler
from SSLproxy import ConnectHTTPSHandler

# --------------------------------------------------------------

DEFAULT_AGENT = "Mozilla/4.0 (compatible; MSIE 5.5; Windows 98; Win 9x 4.90)"

# --------------------------------------------------------------

class Cache(object) :
    def __init__( self, directory=None ) :
        self._directory = directory
        if self._directory == None :
            self._directory = '.'
        self._cachedir = os.path.join(self._directory,'.cache')
        if not(os.path.exists(self._cachedir)) :
            os.makedirs(self._cachedir)

    def _get_cachefile( self, url ) :
        hexurl = hashlib.md5(url).hexdigest()
        return os.path.join( self._cachedir, hexurl ) 

    def get( self, url ) :
        content = None
        cachefile = self._get_cachefile( url )
        if os.path.exists( cachefile ) :
            handle = open( cachefile, 'rb' )
            content = handle.read()
            handle.close()
        return content

    def set( self, url, content ) :
        cachefile = self._get_cachefile( url )
        handle = open( cachefile, 'wb' )
        handle.write( content )
        handle.close()

# --------------------------------------------------------------

class AppURLopener(urllib.FancyURLopener):
    def __init__(self, version, *args):
        self.version = version
        urllib.FancyURLopener.__init__(self, *args)

# --------------------------------------------------------------

class WebUrllib(object) :
    def __init__( self, agent = DEFAULT_AGENT, http_proxy=None  ) :
        # http_proxy is not used now.

        self._agent = agent
        urllib._urlopener = AppURLopener(agent)

    def get ( self, url, file=None, encoding='utf-8' ) :
        result = ""
        url = url.encode(encoding)
        try :
            if file == None :
                f = urllib.urlopen( url )
                for line in f.readlines() :
                    result += line
            else :
                result = urllib.urlretrieve( url, file )
                result = result[0]
        except IOError :
            pass
        except socket.error :
            pass
        return result

    def post(self, *args, **kwargs) :
        raise Exception("Not Implemented")

    def cookies(self) :
        return None

# --------------------------------------------------------------

class WebUrllib2(object) :
    _default_result = None
    
    def __init__( self, agent = DEFAULT_AGENT, http_proxy=None, cache=None, sleep_on_get=None ) :
        self._agent = agent
        self._cache = None
        self._sleep_on_get = sleep_on_get
        if cache :
            cachedir = None
            if type(cache) in (type(''),type(u'')) :
                cachedir = cache
            self._cache = Cache(cachedir)
        
        openers = []

        proxy_support = None
        if http_proxy is not None :
            # Look like urllib2 default proxy works better than ConnectHTTPHandler
            #openers.append(ConnectHTTPHandler(proxy="%s:%s" % (http_proxy[0],http_proxy[1]),debuglevel=1))
            openers.append(urllib2.ProxyHandler({"http" : "http://%s:%s" % (http_proxy[0],http_proxy[1])}))

            openers.append(ConnectHTTPSHandler(proxy="%s:%s" % (http_proxy[0],http_proxy[1])))


        self._cookiejar = cookielib.LWPCookieJar()
        openers.append(urllib2.HTTPCookieProcessor(self._cookiejar))

        opener = urllib2.build_opener(*openers)
        urllib2.install_opener(opener)

    def get ( self, url, postargs=None, getargs=None, file=None, encoding='utf-8', cookie=None, nocache=False ) :
        result = self._default_result

        if getargs != None :
            getargs_data = urllib.urlencode(getargs)
            if '?' in url :
                url += '&' + getargs_data
            else : 
                url += '?' + getargs_data

        url = url.encode(encoding)
        if self._cache and not(nocache):
            cached_content = self._cache.get(url)
            if cached_content is not None :
                result = cached_content
                return result 

        postdata = None

        if postargs != None :
            postdata = urllib.urlencode(postargs)

        header = {'User-agent' : self._agent}
        if cookie :
            header['Cookie']=cookie

        #print self._cookiejar
        #print url
        request = urllib2.Request(url, postdata, header)

        #print "[ %s ]" % self._cookiejar._cookies_for_request(request)
        self._cookiejar.add_cookie_header(request)


        try :
            f = urllib2.urlopen( request )
            if file != None :
                MAXSIZE = 8192*8
                tembuffer = f.read(MAXSIZE)
                handle = open(file,'wb')
                while tembuffer != '' :
                    handle.write(tembuffer)
                    tembuffer = f.read(MAXSIZE)
                handle.close()
                result = file
            else :
                result = f.read()
                if self._cache and result and len(result)>0 and not(nocache) :
                    self._cache.set( url, result )
            if self._sleep_on_get is not None :
                time.sleep(self._sleep_on_get)
        except IOError :
            # print "IOError"
            pass
        except socket.error :
            # print "socket.error"
            pass
        return result

    def post ( self, *args, **kwargs ) :
        return self.get(*args,**kwargs)

    def cookies(self) :
        return self._cookiejar

# --------------------------------------------------------------

class WebDeprecated( WebUrllib2 ) :
    _default_result = ""

Web = WebUrllib2

# --------------------------------------------------------------

if __name__ == "__main__" :
    web = Web()
    print "%s\n-------------------" % web.get("http://giss.mine.nu/")

# --------------------------------------------------------------
