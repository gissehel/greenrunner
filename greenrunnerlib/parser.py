#!/usr/bin/env python
#encoding:utf-8

from webrip import QuickWebRip
from greenrunnerlib.reportGenerator import ReportGenerator
import posixpath
import re
import os
import time
import codecs
import subprocess

class Parser(QuickWebRip) :
    """Parser's role is to parse and/or execute green pepper pages."""
    
    # Login url
    login_url = 'dologin.action'
    
    # Green pepper execution url 
    runaction_url = 'greenpepper/Run.action'
    
    # Green pepper viewpage url
    viewpage_url = 'pages/viewpage.action?pageId=%s'
    
    # regexp object to extract information about a test page
    re_register_spec = re.compile(r'''conf_greenPepper.registerSpecification\((.*?)\).*?align="absmiddle" title="(.*?)"''',re.M+re.S)
    
    # regexp pattern to extract sut information about a test page. It's not with other informations.
    reg_sutInfo_pattern = '''<span id="conf_sutInfo_display_%s_%s_%s" style="display:none">(.*?)</span>'''
    
    # regexp object used to extract page title.
    re_get_title = re.compile(r'''<title>(.*?)</title>''')
    
    # regexp object to extract results about a test page execution
    re_find_result = re.compile(r'''getSpecification\(([^\)]*?)\)\.registerResults\(([^\)]*?)\)''')
    
    # regexp object used to extractthe url of a test page
    re_external_link = re.compile(r'''<meta name="external-link" content="([^"]+)"/>''')
 
    def __init__(self) :
        """Constructor"""
        # Call the mother class constructor with the configuration filename.
        QuickWebRip.__init__(self,'greenrunner.txt')

        # Verbose mode on by default
        self._verbose = True
        
        # The container for report formatters
        self._report_generator = ReportGenerator()

        # the error output        
        self._error_output = ''
        
        # True if there is at least one filter
        self._has_filter = False

        # numeric filters
        self._numeric_filters = []
        
        # title filters
        self._title_filters = []
        
        # .Net mode
        self._dotnet = False

    def add_numeric_filter(self, count) :
        self._has_filter = True
        self._numeric_filters.append(count)

    def add_title_filter(self, pattern) :
        self._has_filter = True
        self._title_filters.append(pattern)
        
    def set_login( self, login ) :
        self._login = login
        
    def set_password( self, password ) :
        self._password = password
        
    def set_gproot( self, gproot ) :
        self._gproot = gproot
        
    def set_verbose( self, verbose ) :
        self._verbose = verbose
        
    def set_gp_commandline( self, commandline ) :
        self._commandline = commandline
        
    def set_dotnet( self, dotnet ) :
        self._dotnet = dotnet
        
    def get_report_generator( self ) :
        return self._report_generator
        
    def login(self) :
        """login the current web instance on the web site."""

        if self._gproot is None :
            raise Exception(_("No Green Pepper root web server provided. Where should I connect ?"))

        # Post the login on the login url.
        result = self._web.post(posixpath.join(self._gproot, self.login_url),postargs={'os_username':self._login,'os_password':self._password},nocache=True)
        
        if result is None :
            raise Exception(_("login impossible. Proxy problem ? Web server problem ?"))
        if "logout.action" not in result :
            raise Exception(_("Authentification failed. Check your login/password."))

    def log(self, string) :
        """Log a string on stdout. Usefull to check what the software is doing."""

        if self._verbose :
            current_time = time.localtime()
            print (u'''[%04d-%02d-%02d %02d:%02d:%02d] %s''' % (current_time.tm_year, current_time.tm_mon, current_time.tm_mday,current_time.tm_hour, current_time.tm_min, current_time.tm_sec, string)).encode('utf-8')
        
    def find_between(self, data, start_data, stop_data) :
        start_index = data.find(start_data)
        stop_index = data.find(stop_data, start_index+len(start_data))
        if start_index == -1 :
            return None
        if stop_index == -1 :
            return None
        return data[start_index+len(start_data):stop_index]

    def get_test_results(self, index_content) :
        """Execute a serie of tests. 
            Take as input a page containing the serie of tests to execute
            and the directory to put the subpages. 
            
            Returns an iterable on test-results. 
            (by yielding them, it can be iterate only once)."""
        
        # Keys associated to the values found in the javascript calls to register(...)
        register_keys = [ 'bulkUID', 'executionUID', 'ctx', 'imgFile', 'spaceKey', 'pageId', 'fieldId', 'javascript_action', 'title' ]
        
        tmp_dirname = 'greenrunner_tmp'

        # Folder is created if not exists
        if not(os.path.exists(tmp_dirname)) :
            os.makedirs(tmp_dirname)
        else :
            for filename in os.listdir(tmp_dirname) :
                os.unlink(os.path.join(tmp_dirname, filename))
        
        count = 0
        
        # For each "page_desc" corresponding the a test page description
        for page_desc, title in self.re_register_spec.findall(index_content) :
            count+=1
            
            # Sepration of fileds in "page_desc", and remove space and quote around each field if present.
            page_desc_splitted = map(lambda s:s.strip(' ').strip("'"), page_desc.split(','))
            
            # Rearranging lists like [ 'bulkUID', 'executionUID', 'ctx', ... ] and [ 'PAGE', '256_1', '', ... ] into [('bulkUID','PAGE'),('executionUID','256_1'),('ctx',''),...] and then we create a dictonnary with those pairs key/values.
            params = dict(zip(register_keys, page_desc_splitted))
            
            if self._has_filter :
                if (count not in self._numeric_filters) and all(pattern.lower() not in title.lower() for pattern in self._title_filters) :
                    continue
            
            # Adding few values to the params as needed by the post url to execute the test page
            params['decorator'] = 'none'
            params['implemented'] = 'false'
            params['isMain'] = 'false'
            # Recuperation of the last information not with others.
            params['sutInfo'] = re.findall( self.reg_sutInfo_pattern%(params['bulkUID'],params['executionUID'],params['fieldId']), index_content )[0]
            
            # Removing of "javascript_action" that doesn't need to be posted
            del params['javascript_action']
            
            if self._commandline is not None :
                url = posixpath.join(self._gproot, self.viewpage_url) % (params['pageId'],)
                sourcecontent_page = self._web.get( url=url ).decode('utf-8')
                
                raw_page_filename = 'raw_%s_%s_%s.html' % (params['bulkUID'],params['executionUID'],params['fieldId'])
                raw_page_full_filename = os.path.join(tmp_dirname,raw_page_filename)
                
                source_page_filename = 'source_%s_%s_%s.html' % (params['bulkUID'],params['executionUID'],params['fieldId'])
                source_page_full_filename = os.path.join(tmp_dirname,source_page_filename)
                
                
                with codecs.open(source_page_full_filename,'wb',encoding='utf-8') as handle :
                    handle.write(self.find_between(sourcecontent_page, '<!-- wiki content -->', '<!--\n<rdf:RDF'))
                title = self.find_between(sourcecontent_page, 'dc:title="', '"')
                url = self.find_between(sourcecontent_page,'rdf:about="','"')
                ### 

                args.replace('{source}',source_page_full_filename) 
                args.replace('{output}',raw_page_full_filename) 

                args = self._commandline.split('|')
                # args.append(source_page_full_filename)
                # args.append(raw_page_full_filename)
                subprocess.Popen( args, stdout=subprocess.PIPE, stderr=subprocess.PIPE ).communicate()
                
                output_encoding = 'utf-8'
                if self._dotnet :
                	output_encoding = 'Windows-1252'
                
                with codecs.open(raw_page_full_filename,'rb',encoding=output_encoding) as handle :
                    content_raw = handle.read()

                os.unlink(raw_page_full_filename)
                os.unlink(source_page_full_filename)
                
                result = {
                        'content_page' : self.find_between(content_raw,'<results><![CDATA[',']]></results>'),
                        'id' : params['fieldId'],
                        'count' : count,
                        'title' : title,
                        'url' : url,
                        'sut' : params['sutInfo'],
                        # Ok, here I should use an XML API.
                        'success' : int(self.find_between(content_raw,'<success>','</success>')),
                        'failures' : int(self.find_between(content_raw,'<failure>','</failure>')), # if count != 5 else 6,
                        'errors' : int(self.find_between(content_raw,'<error>','</error>')), # if count != 8 else 3,
                        'ignored' : int(self.find_between(content_raw,'<ignored>','</ignored>')), # if count != 3 else 1,
                        }
                result['results'] = None
                
                
            else : 
                
                try :
                    # Posting params on the web site to execute the test and store the result
                    content_page = self._web.get( url=posixpath.join(self._gproot, self.runaction_url), postargs=params )
                    if content_page is None :
                        raise IOError()
                
                    content_page = content_page.decode('utf-8') if content_page is not None else u''
                    
                    # Getting title and url of the page from execution result.
                    title = self.get_title(content_page)
                    url = self.get_url(content_page)
                    
                    # Getting execution result (number of succes, number of failure, number of errors, number of ignored)
                    page_key, page_result = self.re_find_result.findall(content_page)[0]
                    page_key_splitted = map(lambda s:s.strip(' ').strip("'"), page_key.split(','))
                    page_result_splitted = map(lambda s:s.strip(' ').strip("'"), page_result.split(','))
                
                    if url is None :
                      url = posixpath.join(self._gproot, self.viewpage_url) % (params['pageId'],)
                    
                    # The result yield is just a dictionnary with all informations needed and preparsed.
                    result = {
                        'content_page' : content_page,
                        'id' : params['fieldId'],
                        'count' : count,
                        'title' : title,
                        'url' : url,
                        'sut' : params['sutInfo'],
                        'results' : page_result_splitted,
                        'success' : int(page_result_splitted[1]),
                        'failures' : int(page_result_splitted[2]), # if count != 5 else 6,
                        'errors' : int(page_result_splitted[3]), # if count != 8 else 3,
                        'ignored' : int(page_result_splitted[4]), # if count != 3 else 1,
                        }
                except IOError :
                    url = posixpath.join(self._gproot, self.viewpage_url) % (params['pageId'],)
                    result = {
                        'content_page' : _('Connection failed'),
                        'id' : params['fieldId'],
                        'count' : count,
                        'title' : title,
                        'url' : url,
                        'sut' : params['sutInfo'],
                        'results' : None,
                        'success' : 0,
                        'failures' : 1, # if count != 5 else 6,
                        'errors' : 0, # if count != 8 else 3,
                        'ignored' : 0, # if count != 3 else 1,
                        }

            # We define here what "all ok" mean...
            result['allok'] = (result['success'] != 0) and (result['failures'] == 0) and (result['errors'] == 0)
            # We define here what "no errors" mean
            result['noerrors'] = (result['failures'] == 0) and  (result['errors'] == 0)
            
            # Logging on stdout in case the one who launched the test got bored.
            current_log = "%s %4d %s (%d, %d, %d, %d)" % ( "    " if result['noerrors'] else "[KO]", result['count'], result['title'], result['success'], result['failures'], result['errors'], result['ignored'] )
            if not(result['allok']) :
                self._error_output += current_log
                self._error_output += '\n'
            self.log(current_log)
            
            # Yielding result
            yield result

        for filename in os.listdir(tmp_dirname) :
            os.unlink(os.path.join(tmp_dirname, filename))
        os.rmdir(tmp_dirname)
    
    def run_tag_page(self, page_id) :
        """Execute a serie of tests and generate report
            Take as input :
            - The page id containing the serie of tests
            - The main report name
            - The folder to place the page per page reports
            """

        # First we login on the site
        self.login()
        
        self._error_output = ''
        summury_page_url = posixpath.join(self._gproot, self.viewpage_url) % (page_id,)
        # Getting web page content
        index_content = self._web.get( url=summury_page_url )
        
        if index_content is None :
            raise Exception(_("No test page found for the id [%s]") % page_id)
        
        # Getting page title
        main_title = self.get_title(index_content).decode('iso-8859-1')

        # Writting header in both pages
        
        self._report_generator.set_title(main_title)
        
        # Writting title and generation date and time.
        self._report_generator.set_current_time(time.localtime())
        self._report_generator.set_runmode( _("Run mode") , _("Distant run") if (self._commandline is None) else _("Local run"))
        self._report_generator.set_sourcepage(_("Based on page"),summury_page_url)
        
        # And the main big table...
        self._report_generator.start_tests()
        
        # total will contains sums from results.
        total = {
            'success' : 0,
            'failures' : 0,
            'errors' : 0,
            'ignored' : 0,
            }
        
        # Iteration threw tests results.
        for result in self.get_test_results(index_content) :
            # For each test result, a line is put in each report
            self._report_generator.add_test_result(result)
            
            # Updating total stucture...
            total['success'] += result['success']
            total['failures'] += result['failures']
            total['errors'] += result['errors']
            total['ignored'] += result['ignored']
        
        # On the end, we put the total line...
        self._report_generator.set_total_result(total)
        
        # And we close the table.
        self._report_generator.stop_tests()
        
        self._report_generator.close()
        
        execution_ok = False
        if (total['failures']==0) and (total['errors']==0) :
            execution_ok = True

        if not(execution_ok) :
            if self._verbose :
                print (u'''\n%s\n\n%s''' % ('=' * 50, self._error_output)).encode('utf-8')
        
        return execution_ok

    def get_title(self, content) :
        """Get the title of an html page."""
        titles = self.re_get_title.findall(content)
        if len(titles) == 0 :
            return '?'
        return titles[0]

    def get_url(self, content) :
        """Get the url of a test page."""
        urls = self.re_external_link.findall(content)
        if len(urls) == 0 :
            return None
        return urls[0]

