import os
import web 
import yaml

class QuickWebRip(object) :
    def __init__(self,config_file=None) :
        self._config_file = config_file
        if os.path.exists(self._config_file) :
            with open(self._config_file,'rt') as handle :
                self._config = yaml.load(handle.read())
        else :
            self._config = {}
        use_cache = self.get_config('cache',False)
        
        sleep_on_get = self.get_config('sleep_on_get',None)
        # print("Use cache : [%s]" % (use_cache,))
        # print("Sleep on get : [%s]" % (sleep_on_get,))
        self._web = web.Web(cache=use_cache,sleep_on_get=sleep_on_get)

    def get_config(self, key, default=None) :
        return self._config.get(key,default)

    def resolv_url(self, *args, **kwargs) :
        return self._web.resolv_url(*args, **kwargs)
