import codecs
import os
from style import header, footer, flipflopjs

class ReportGenerator(object) :
    def __init__(self) :
        self._formatters = []
        self._closed = False
        
    def add_formatter(self, formatter) :
        self._formatters.append(formatter)

    def close(self) :
        if not(self._closed) :
            for formatter in self._formatters :
                formatter.close()
            self._closed = True

    def delegation(self, name, args, kwargs) :
        for formatter in self._formatters :
            getattr(formatter,name)(*args, **kwargs)

    def set_title(self, *args, **kwargs) : self.delegation('set_title', args, kwargs)
    def set_current_time(self, *args, **kwargs) : self.delegation('set_current_time', args, kwargs)
    def set_runmode(self, *args, **kwargs) : self.delegation('set_runmode', args, kwargs)
    def set_sourcepage(self, *args, **kwargs) : self.delegation('set_sourcepage', args, kwargs)
    
    def start_tests(self, *args, **kwargs) : self.delegation('start_tests', args, kwargs)
    def stop_tests(self, *args, **kwargs) : self.delegation('stop_tests', args, kwargs)
    
    def add_test_result(self, *args, **kwargs) : self.delegation('add_test_result', args, kwargs)
    def set_total_result(self, *args, **kwargs) : self.delegation('set_total_result', args, kwargs)
        

class ReportFormatter(object) :
    def __init__(self) :
        self._handle = None
        self._closed = False

    def write(self, content) :
        if self._handle is not None :
            self._handle.write(content)
        
    def write_javascript(self) :
        pass

    def set_title(self, title) : 
        self.write(header % {'title': title})
        self.write_javascript()
        self.write('''<h1 class="main-title">%s</h1>\n''' % (title, ))

    def set_current_time(self, current_time) :
        self.write('''<h2 class="generation-date">%s : %04d-%02d-%02d %02d:%02d:%02d</h2>\n''' % (_("Generation"), current_time.tm_year, current_time.tm_mon, current_time.tm_mday, current_time.tm_hour, current_time.tm_min, current_time.tm_sec))

    def set_runmode(self, runmode_label, runmode_value) :
        self.write('''<div class="execution-type">%s : %s</div>\n''' % (runmode_label,runmode_value))
        
    def set_sourcepage(self, sourcepage_label, sourcepage_value) :
        self.write('''<div class="testlist-link">%s <a href="%s">%s</a></div>\n''' % (sourcepage_label,sourcepage_value,sourcepage_value))
        
    def start_tests(self) :
        self.write('''<table class="conf_specificationList green_accordion">\n''')
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
        self.write(line)

    def stop_tests(self) :
        self.write('''</table>\n''')
        self.write(footer % {'footer_message':_('Page generated by %s') % '<a href="http://code.google.com/p/greenrunner">GreenRunner</a>'})
        
        
    def add_test_result(self, result) :
        self.write(self.format_main_result_line(result, True))

    def set_total_result(self, total) :
        self.write(self.format_total_result_line(total))
        
    def close(self) :
        if not(self._closed) :
            if self._handle is not None :
                self._handle.close()
            self._closed = True

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

class FileReportFormatter(ReportFormatter) :
    def __init__(self, filename) :
        super(FileReportFormatter, self).__init__()
        self._filename = filename
        self._handle = codecs.open(self._filename,'wb',encoding='utf-8')
        
class FileInDirReportFormatter(FileReportFormatter) :
    pass

class FullReportFormatter(FileReportFormatter) :
    def write_javascript(self) :
        # Writting the "flipflop" and javascript sugar on the main report
        self.write(flipflopjs % (_("Loading in progress..."),_("Complete"),_("Partial"),_("Errors")))

class ErrorReportFormatter(FullReportFormatter) :
    def add_test_result(self, result) :
        if result['allok'] :
            return
        super(ErrorReportFormatter, self).add_test_result(result)

class DirReportFormatter(ReportFormatter) :
    def __init__(self, dirname) :
        super(DirReportFormatter, self).__init__()
        self._dirname = dirname
        self.clean_dir()
        self._index_filename = os.path.join(self._dirname,'index.html')
        self._handle = codecs.open(self._index_filename,'wb',encoding='utf-8')
        self._handle_test = None
        self._run_uid = None
        self._current_time = None
        self._runmode_label = None
        self._runmode_value = None
        
    def set_current_time(self, current_time) :
        super(DirReportFormatter, self).set_current_time(current_time)
        self._run_uid = "%04d%02d%02d-%02d%02d%02d" % (current_time.tm_year, current_time.tm_mon, current_time.tm_mday, current_time.tm_hour, current_time.tm_min, current_time.tm_sec)
        self._current_time = current_time
        
    def set_runmode(self, runmode_label, runmode_value) :
        super(DirReportFormatter, self).set_runmode(runmode_label, runmode_value)
        ( self._runmode_label, self._runmode_value ) = ( runmode_label, runmode_value )
        
    def clean_dir(self) :
        # Folder is created if not exists
        if not(os.path.exists(self._dirname)) :
            os.makedirs(self._dirname)
        else :
            for filename in os.listdir(self._dirname) :
                os.unlink(os.path.join(self._dirname, filename))

    def add_test_result(self, result) :
        result['filename'] = 'result_%s_%04d.html' % ( self._run_uid, result['count'] )
        
        full_filename = os.path.join( self._dirname, result['filename'] )
        
        report_formatter = FileInDirReportFormatter(full_filename)
        report_formatter.set_title( result['title'] )
        report_formatter.set_current_time( self._current_time )
        report_formatter.set_runmode( self._runmode_label, self._runmode_value )
        report_formatter.set_sourcepage( _("Based on page"), result['url'] )
        
        report_formatter.start_tests()
        report_formatter.add_test_result(result)
        report_formatter.stop_tests()
        report_formatter.close()
        
        self.write(self.format_main_result_line(result, False))
