#!/usr/bin/env python
from __future__ import with_statement
from webrip import QuickWebRip
from web import ResolvUrl
from style import header, footer
import optparse
import re
import os
import sys
import time
import posixpath

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
            raise Exception("login impossible. Proxy problem ? Web server problem ?")
        if "logout.action" not in result :
            raise Exception("Authentification failed. Check your login/password.")
        
    def log(self, string) :
        """Log a string on stdout. Usefull to check what the software is doing."""

        if self._verbose :
            current_time = time.localtime()
            print '''[%04d-%02d-%02d %02d:%02d:%02d] %s''' % (current_time.tm_year, current_time.tm_mon, current_time.tm_mday,current_time.tm_hour, current_time.tm_min, current_time.tm_sec, string)
        
    def run(self) :
        """Main entry point for the class."""
        
        # Command line parsing
        parser = optparse.OptionParser()
        parser.add_option('-i', '--pageid', 
                          dest="pageid", 
                          default="11337747",
                          type="int",
                          help="L'index de la page a executer",
                          )
        parser.add_option('-o', '--output',
                          dest="output_filename",
                          default="result.html",
                          action="store",
                          help="Le nom du fichier rapport",
                          )
        parser.add_option('-d', '--dir',
                          dest="output_directory",
                          default="result",
                          action="store",
                          help="Le nom du dossier rapport page a page",
                          )
        parser.add_option('-v', '--verbose',
                          dest="verbose",
                          default=True,
                          action="store_true",
                          help="Mode verbose",
                          )
        parser.add_option('-q', '--quiet',
                          dest="verbose",
                          action="store_false",
                          help="Mode quiet",
                          )
        parser.add_option('-l', '--login',
                          dest="login",
                          default=None,
                          action="store",
                          help="login",
                          )
        parser.add_option('-p', '--password',
                          dest="password",
                          default=None,
                          action="store",
                          help="password",
                          )
        parser.add_option('-r','--greenpepper-root',
                          dest='gproot',
                          default=None,
                          action="store",
                          help="Root of GP site",
                          )
        options, remainder = parser.parse_args()

        # Le mode verbose can be changed from command line        
        self._verbose = options.verbose
        
        # Login can be put in the configuration file, and overridden with the commande line.
        self._login = self.get_config('login') if (options.login is None) else options.login
        
        # Password can be put in the configuration file, and overridden with the commande line.
        self._password = self.get_config('password') if (options.password is None) else options.password
 
        # Green pepper root can be put in the configuration file, and overridden with the commande line.
        self._gproot = self.get_config('gproot') if (options.gproot is None) else options.gproot

        if self._gproot is None :
            raise Exception("No Green Pepper root web server provided. Where should I connect ?")

        # Login on the web server.
        self.login()
        
        if not( self.run_tag_page( options.pageid, options.output_filename, options.output_directory ) ) :
            sys.exit(1)

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
            
            # Posting params on the web site to execute the test and store the result
            content_page = self._web.get( url=posixpath.join(self._gproot, self.runaction_url), postargs=params )
            
            # Getting title and url of the page from execution result.
            title = self.get_title(content_page)
            url = self.get_url(content_page)
            
            # Getting execution result (number of succes, number of failure, number of errors, number of ignored)
            page_key, page_result = self.re_find_result.findall(content_page)[0]
            page_key_splitted = map(lambda s:s.strip(' ').strip("'"), page_key.split(','))
            page_result_splitted = map(lambda s:s.strip(' ').strip("'"), page_result.split(','))
            
            # self.log(title)
            # Saving result page in it's own file
            page_filename = 'result_%s_%s_%s.html' % (params['bulkUID'],params['executionUID'],params['fieldId'])
            page_full_filename = os.path.join(output_dirname,page_filename)
            with open(page_full_filename,'wb') as handle :
                handle.write(header % {'title':title})
                handle.write(content_page)
                handle.write(footer)

            # The result yield is just a dictionnary with all informations needed and preparsed.
            result = {
                'content_page' : content_page,
                'id' : params['fieldId'],
                'title' : title,
                'filename' : page_filename,
                'url' : url,
                'sut' : params['sutInfo'],
                'results' : page_result_splitted,
                'success' : int(page_result_splitted[1]),
                'failures' : int(page_result_splitted[2]), # if count != 5 else 6,
                'errors' : int(page_result_splitted[3]), # if count != 8 else 3,
                'ignored' : int(page_result_splitted[4]), # if count != 3 else 1,
                }
            # We define here what "all ok" mean...
            result['allok'] = (result['success'] != 0) and (result['failures'] == 0) and (result['errors'] == 0)
            # We define here what "no errors" mean
            result['noerrors'] = (result['failures'] == 0) and  (result['errors'] == 0)

            # Logging on stdout in case the one who launched the test got bored.
            self.log("%s %s (%d, %d, %d, %d)" % ( "    " if result['noerrors'] else "[KO]", title, result['success'], result['failures'], result['errors'], result['ignored'] ))
            
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

        # Getting web page content
        index_content = self._web.get( url=posixpath.join(self._gproot, self.viewpage_url) % (page_id,) )
        
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
        with open(output_filename,'wb') as handle_total :
            with open(output_index_filename,'wb') as handle_index :
                # Writting header in both pages
                self.write(handle_total, handle_index, header % {'title': main_title})

                # Writting the "flipflop" and javascript sugar on the main report
                handle_total.write("""<script type='text/javascript'>
                    jQuery(function($){ 
                        var $body = $('body');
                        $('.green_accordion > tbody').accordion({ collapsible : true,  animated: false, active : false, autoHeight: false });
                        $('.main-title').click(function(){
                            if ($body.hasClass('hide-allok')) {
                                $body.removeClass('show-all');
                                $body.removeClass('hide-allok');
                                $body.addClass('show-onlyerrors');
                            } else {
                                if ($body.hasClass('show-onlyerrors')) {
                                    $body.removeClass('hide-allok');
                                    $body.removeClass('show-onlyerrors');
                                    $body.addClass('show-all');
                                } else {
                                    $body.removeClass('show-all');
                                    $body.removeClass('show-onlyerrors');
                                    $body.addClass('hide-allok');
                                }
                            }
                        });
                        $('#filter-complete').click(function(){
                                    $body.addClass('show-all');
                                    $body.removeClass('hide-allok');
                                    $body.removeClass('show-onlyerrors');
                        });
                        $('#filter-partial').click(function(){
                                    $body.removeClass('show-all');
                                    $body.addClass('hide-allok');
                                    $body.removeClass('show-onlyerrors');
                        });
                        $('#filter-error').click(function(){
                                    $body.removeClass('show-all');
                                    $body.removeClass('hide-allok');
                                    $body.addClass('show-onlyerrors');
                        });
                        $('.test-link a').click(function(e){
                            window.open($(this).attr('href'));
                            e.preventDefault();
                        });
                        $('.loading').slideUp(1500, function() { $body.addClass('show-all'); });
                    })</script>
                    <div class='loading'><div class='loading-text'>%s</div></div>
                    <div class='multichoices'><div id='filter-complete' class='choice'>%s</div><div id='filter-partial' class='choice'>%s</div><div id='filter-error' class='choice'>%s</div></div>
                    """ % ("Chargement en cours...","Complet","Partiel","Erreurs"))
                
                # Writting title and generation date and time.
                self.write(handle_total, handle_index, '''<h1 class="main-title">%s</h1>\n''' % (main_title, ))
                self.write(handle_total, handle_index, '''<h2 class="generation-date">%s : %04d-%02d-%02d %02d:%02d:%02d</h2>\n''' % ("Generation", current_time.tm_year, current_time.tm_mon, current_time.tm_mday,current_time.tm_hour, current_time.tm_min, current_time.tm_sec))
                
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
                self.write(handle_total, handle_index, footer)
                
                if (total['failures']==0) and (total['errors']==0) :
                    execution_ok = True
        return execution_ok

    def write(self, handle1, handle2, value) :
        """Ecrit dans deux fichiers a la fois"""
        handle1.write(value)
        handle2.write(value)

    def format_header_line(self) :
        line = '''<tr class="header-line"><th class="test-id">%s</th><th class="test-title">%s</th><th class="test-link">%s</th><th class="test-success">%s</th><th class="test-failures">%s</th><th class="test-errors">%s</th><th class="test-ignored">%s</th><th class="test-sut">%s</th></tr><tr class="sub-header-line"></tr>\n''' % (
            'No',
            'Titre',
            'Lien',
            'Succes',
            'Echec',
            'Erreur',
            'Ignore',
            'Environnement execution',
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
            'Total',
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

