#!/usr/bin/env python
#encoding:utf-8
from __future__ import with_statement
from webrip import QuickWebRip
from web import ResolvUrl
from style import header, footer, flipflopjs
import optparse
import re
import os
import sys
import time
import posixpath
import gettext
import codecs
import locale
import subprocess

# Set up message catalog access
gettext.install('greenrunner',os.path.join(os.path.dirname(sys.argv[0]),'locale'),unicode=True,names=['ngettext'])

class GreenRunner(QuickWebRip) :
    """GreenRunner class can generate reports from an execution of a serie of tests contained in a green pepper page."""
    
    # Login url
    login_url = 'dologin.action'
    
    # Green pepper execution url 
    runaction_url = 'greenpepper/Run.action'
    
    # Green pepper viewpage url
    viewpage_url = 'pages/viewpage.action?pageId=%s'
    
    # regexp object to extract information about a test page
    re_register_spec = re.compile(r'''conf_greenPepper.registerSpecification\((.*?)\)''')
    
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
        
    def login(self) :
        """login the current web instance on the web site."""

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
        
    def run(self) :
        """Main entry point for the class."""
        
        # Command line parsing
        parser = optparse.OptionParser()
        parser.add_option('-i', '--pageid', 
                          dest="pageid", 
                          default="11337747",
                          type="int",
                          help=_("Page id to execute"),
                          )
        parser.add_option('-o', '--output',
                          dest="output_filename",
                          default="result.html",
                          action="store",
                          help=_("Report filename"),
                          )
        parser.add_option('-d', '--dir',
                          dest="output_directory",
                          default="result",
                          action="store",
                          help=_("Report folder name"),
                          )
        parser.add_option('-v', '--verbose',
                          dest="verbose",
                          default=True,
                          action="store_true",
                          help=_("Verbose mode"),
                          )
        parser.add_option('-q', '--quiet',
                          dest="verbose",
                          action="store_false",
                          help=_("Quiet mode"),
                          )
        parser.add_option('-l', '--login',
                          dest="login",
                          default=None,
                          action="store",
                          help=_("Login"),
                          )
        parser.add_option('-p', '--password',
                          dest="password",
                          default=None,
                          action="store",
                          help=_("Password"),
                          )
        parser.add_option('-r','--greenpepper-root',
                          dest='gproot',
                          default=None,
                          action="store",
                          help=_("Root of GP site"),
                          )
        parser.add_option('-L', '--lang',
                          dest="lang",
                          default=None,
                          action="store",
                          help=_("Language"),
                          )
        parser.add_option('-c', '--command-line',
                          dest="commandline",
                          default=None,
                          action="store",
                          help=_("Command line for local execution"),
                          )
        options, remainder = parser.parse_args()

        if not(options.lang is None):
            os.environ['LANGUAGE'] = options.lang
            gettext.install('greenrunner',os.path.join(os.path.dirname(sys.argv[0]),'locale'),unicode=True,names=['ngettext'])

        # Le mode verbose can be changed from command line        
        self._verbose = options.verbose
        
        # Login can be put in the configuration file, and overridden with the commande line.
        self._login = self.get_config('login') if (options.login is None) else options.login
        
        # Password can be put in the configuration file, and overridden with the commande line.
        self._password = self.get_config('password') if (options.password is None) else options.password
 
        # Green pepper root can be put in the configuration file, and overridden with the commande line.
        self._gproot = self.get_config('gproot') if (options.gproot is None) else options.gproot

        # Green pepper root can be put in the configuration file, and overridden with the commande line.
        self._commandline = self.get_config('commandline') if (options.commandline is None) else options.commandline

        if self._gproot is None :
            raise Exception(_("No Green Pepper root web server provided. Where should I connect ?"))

        # Login on the web server.
        self.login()
        
        if not( self.run_tag_page( options.pageid, options.output_filename, options.output_directory ) ) :
            sys.exit(1)

    def find_between(self, data, start_data, stop_data) :
        start_index = data.find(start_data)
        stop_index = data.find(stop_data, start_index+len(start_data))
        if start_index == -1 :
            return None
        if stop_index == -1 :
            return None
        return data[start_index+len(start_data):stop_index]
    def get_test_results(self, index_content, output_dirname) :
        """Execute a serie of tests. 
            Take as input a page containing the serie of tests to execute
            and the directory to put the subpages. 
            
            Returns an iterable on test-results. 
            (by yielding them, it can be iterate only once)."""
        
        # Keys associated to the values found in the javascript calls to register(...)
        register_keys = [ 'bulkUID', 'executionUID', 'ctx', 'imgFile', 'spaceKey', 'pageId', 'fieldId', 'javascript_action' ]
        
        # count = 0
        
        # For each "page_desc" corresponding the a test page description
        for page_desc in self.re_register_spec.findall(index_content) :
            # count+=1
            
            # Sepration of fileds in "page_desc", and remove space and quote around each field if present.
            page_desc_splitted = map(lambda s:s.strip(' ').strip("'"), page_desc.split(','))
            
            # Rearranging lists like [ 'bulkUID', 'executionUID', 'ctx', ... ] and [ 'PAGE', '256_1', '', ... ] into [('bulkUID','PAGE'),('executionUID','256_1'),('ctx',''),...] and then we create a dictonnary with those pairs key/values.
            params = dict(zip(register_keys, page_desc_splitted))
            
            # Adding few values to the params as needed by the post url to execute the test page
            params['decorator'] = 'none'
            params['implemented'] = 'false'
            params['isMain'] = 'false'
            # Recuperation of the last information not with others.
            params['sutInfo'] = re.findall( self.reg_sutInfo_pattern%(params['bulkUID'],params['executionUID'],params['fieldId']), index_content )[0]
            
            # Removing of "javascript_action" that doesn't need to be posted
            del params['javascript_action']
            
            # Saving result page in it's own file
            report_page_filename = 'result_%s_%s_%s.html' % (params['bulkUID'],params['executionUID'],params['fieldId'])
            report_page_full_filename = os.path.join(output_dirname,report_page_filename)
            
            
            if self._commandline is not None :
                url = posixpath.join(self._gproot, self.viewpage_url) % (params['pageId'],)
                sourcecontent_page = self._web.get( url=url )
                
                raw_page_filename = 'raw_%s_%s_%s.html' % (params['bulkUID'],params['executionUID'],params['fieldId'])
                raw_page_full_filename = os.path.join(output_dirname,raw_page_filename)
                
                source_page_filename = 'source_%s_%s_%s.html' % (params['bulkUID'],params['executionUID'],params['fieldId'])
                source_page_full_filename = os.path.join(output_dirname,source_page_filename)
                
                
                with open(source_page_full_filename,'wb') as handle :
                    handle.write(self.find_between(sourcecontent_page, '<!-- wiki content -->', '<!--\n<rdf:RDF'))
                title = self.find_between(sourcecontent_page, 'dc:title="', '"')
                url = self.find_between(sourcecontent_page,'rdf:about="','"')
                ### 
                    
                args = self._commandline.split('|')
                args.append(source_page_full_filename)
                args.append(raw_page_full_filename)
                p = subprocess.call( args, stdout=subprocess.PIPE, stderr=subprocess.PIPE )

                
                with codecs.open(raw_page_full_filename,'rb',encoding='Windows-1252') as handle :
                    content_raw = handle.read()

                os.unlink(raw_page_full_filename)
                os.unlink(source_page_full_filename)
                
                result = {
                        'content_page' : self.find_between(content_raw,'<results><![CDATA[',']]></results>'),
                        'id' : params['fieldId'],
                        'title' : title,
                        'filename' : report_page_filename,
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
                        'title' : title,
                        'filename' : report_page_filename,
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
                        'title' : url,
                        'filename' : '',
                        'url' : url,
                        'sut' : params['sutInfo'],
                        'results' : None,
                        'success' : 0,
                        'failures' : 1, # if count != 5 else 6,
                        'errors' : 0, # if count != 8 else 3,
                        'ignored' : 0, # if count != 3 else 1,
                        }

            with codecs.open(report_page_full_filename,'wb',encoding='utf-8') as handle :
                handle.write(header % {'title':result['title']})
                handle.write(result['content_page'])
                handle.write(footer % {'footer_message':_('Page generated by %s') % '<a href="http://code.google.com/p/greenrunner">GreenRunner</a>'})

            # We define here what "all ok" mean...
            result['allok'] = (result['success'] != 0) and (result['failures'] == 0) and (result['errors'] == 0)
            # We define here what "no errors" mean
            result['noerrors'] = (result['failures'] == 0) and  (result['errors'] == 0)
            
            # Logging on stdout in case the one who launched the test got bored.
            self.log("%s %s (%d, %d, %d, %d)" % ( "    " if result['noerrors'] else "[KO]", result['title'], result['success'], result['failures'], result['errors'], result['ignored'] ))
            
            # Yielding result
            yield result
    
    def run_tag_page(self, page_id, output_filename, output_dirname) :
        """Execute a serie of tests and generate report
            Take as input :
            - The page id containing the serie of tests
            - The main report name
            - The folder to place the page per page reports
            """

        # Folder is created if not exists
        if not(os.path.exists(output_dirname)) :
            os.makedirs(output_dirname)
        else :
            for filename in os.listdir(output_dirname) :
                os.unlink(os.path.join(output_dirname, filename))

        summury_page_url = posixpath.join(self._gproot, self.viewpage_url) % (page_id,)
        # Getting web page content
        index_content = self._web.get( url=summury_page_url )
        
        if index_content is None :
            raise Exception("No test page found for the id [%s]" % page_id)
        
        # with open(os.path.join(output_dirname,'result-main.html'),'wb') as handle :
        #     handle.write(header)
        #     handle.write(index_content)
        #     handle.write(footer)
        
        # Getting page title
        main_title = self.get_title(index_content)

        # Getting current time
        current_time = time.localtime()
        
        # Creating page per page main report filename
        output_index_filename = os.path.join(output_dirname,'index.html')

        execution_ok = False
        
        # Opening two handles, one for the main report, one for the page per page report.
        with codecs.open(output_filename,'wb',encoding='utf-8') as handle_total :
            with codecs.open(output_index_filename,'wb',encoding='utf-8') as handle_index :
                # Writting header in both pages
                main_title = main_title.decode('iso-8859-1')
                self.write(handle_total, handle_index, header % {'title': main_title})

                # Writting the "flipflop" and javascript sugar on the main report
                handle_total.write(flipflopjs % (_("Loading in progress..."),_("Complete"),_("Partial"),_("Errors")))
                
                # Writting title and generation date and time.
                self.write(handle_total, handle_index, '''<h1 class="main-title">%s</h1>\n''' % (main_title, ))
                self.write(handle_total, handle_index, '''<h2 class="generation-date">%s : %04d-%02d-%02d %02d:%02d:%02d</h2>\n''' % (_("Generation"), current_time.tm_year, current_time.tm_mon, current_time.tm_mday,current_time.tm_hour, current_time.tm_min, current_time.tm_sec))
                self.write(handle_total, handle_index, '''<div class="execution-type">%s : %s</div>\n''' % (_("Run mode"),_("Distant run") if (self._commandline is None) else _("Local run")))
                self.write(handle_total, handle_index, '''<div class="testlist-link">%s <a href="%s">%s</a></div>\n''' % (_("Based on page"),summury_page_url,summury_page_url))
                
                # And the main big table...
                self.write(handle_total, handle_index, '''<table class="conf_specificationList green_accordion">\n''')
                
                # total will contains sums from results.
                total = {
                    'success' : 0,
                    'failures' : 0,
                    'errors' : 0,
                    'ignored' : 0,
                    }
    
                self.write(handle_total, handle_index, self.format_header_line())
                        
                # Iteration threw tests results.
                for result in self.get_test_results(index_content, output_dirname) :
                    # For each test result, a line is put in each report (but sliglty different).
                    handle_total.write(self.format_main_result_line(result, is_total=True))
                    handle_index.write(self.format_main_result_line(result, is_total=False))
                    
                    # Updating total stucture...
                    total['success'] += result['success']
                    total['failures'] += result['failures']
                    total['errors'] += result['errors']
                    total['ignored'] += result['ignored']

                # On the end, we put the total line...
                self.write(handle_total, handle_index, self.format_total_result_line(total))

                # And we close the table.
                self.write(handle_total, handle_index, '''</table>\n''')
                self.write(handle_total, handle_index, footer % {'footer_message':_('Page generated by %s') % '<a href="http://code.google.com/p/greenrunner">GreenRunner</a>'})
                
                if (total['failures']==0) and (total['errors']==0) :
                    execution_ok = True
        return execution_ok

    def write(self, handle1, handle2, value) :
        """Ecrit dans deux fichiers a la fois"""
        handle1.write(value)
        handle2.write(value)

    def format_header_line(self) :
        line = '''<tr class="header-line"><th class="test-id">%s</th><th class="test-title">%s</th><th class="test-link">%s</th><th class="test-success">%s</th><th class="test-failures">%s</th><th class="test-errors">%s</th><th class="test-ignored">%s</th><th class="test-sut">%s</th></tr><tr class="sub-header-line"></tr>\n''' % (
            _('#'),
            _('Title'),
            _('Link'),
            _('Success'),
            _('Failure'),
            _('Error'),
            _('Ignored'),
            _('sut'),
            )
        return line            
        
    def format_main_result_line(self, result, is_total) :
        """Format a result test page execution into a line of html table"""
        
        extraclassname = ''
        if result['allok'] :
            extraclassname += ' allok'
        if result['noerrors'] :
            extraclassname += ' noerrors'
        line = '''<tr class="title-line%s"><td class="test-id %s">%s</td><td class="test-title">%s</td><td class="test-link"><a href="%s"><div class="img-link"></div></a></td><td class="test-success %s">%s</td><td class="test-failures %s">%s</td><td class="test-errors %s">%s</td><td class="test-ignored %s">%s</td><td class="test-sut">%s</td></tr>\n''' % (
            extraclassname,
            'result-success' if (result['noerrors']) else 'result-failure',
            int(result['id'])+1,
            result['title'] if is_total else "<a href='%s'>%s</a>" % (result['filename'],result['title']),
            result['url'],
            'no-value' if result['success']==0 else 'values',
            result['success'],
            'no-value' if result['failures']==0 else 'values',
            result['failures'],
            'no-value' if result['errors']==0 else 'values',
            result['errors'],
            'no-value' if result['ignored']==0 else 'values',
            result['ignored'],
            result['sut'],
            )
        if is_total :
            line += '''<tr class="test-subpage-line%s"><td colspan="8" class="test-subpage">%s</td></tr>''' % (
                extraclassname,
                result['content_page'],
                )
        return line
        
    def format_total_result_line(self, total) :
        """Format the 'total' line into a line of html table"""
        return '''<tr class="total-line"><td colspan="3" class="tests-total %s">%s</td><td class="test-success total %s">%s</td><td class="test-failures total %s">%s</td><td class="test-errors total %s">%s</td><td class="test-ignored total %s">%s</td><td class="test-sut total">%s</td></tr>\n''' % (
            'result-success' if ((total['failures']==0) and (total['errors']==0)) else 'result-failure',
            _('Total'),
            'no-value' if total['success']==0 else 'values',
            total['success'],
            'no-value' if total['failures']==0 else 'values',
            total['failures'],
            'no-value' if total['errors']==0 else 'values',
            total['errors'],
            'no-value' if total['ignored']==0 else 'values',
            total['ignored'],
            '',
            )
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

if __name__ == '__main__' :
    # Instanciate the main class and run it.
    GreenRunner().run()

