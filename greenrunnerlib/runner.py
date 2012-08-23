#!/usr/bin/env python
#encoding:utf-8

import optparse
import os
import sys
import gettext

from greenrunnerlib.reportGenerator import FullReportFormatter
from greenrunnerlib.reportGenerator import DirReportFormatter
from greenrunnerlib.reportGenerator import ErrorReportFormatter
from greenrunnerlib.parser import Parser

# Set up message catalog access
gettext.install('greenrunner',os.path.join(os.path.dirname(sys.argv[0]),'locale'),unicode=True,names=['ngettext'])

class Runner(object) :
    """Runner parse command line and configuration file in order to run what is needed to run. It connect green pepper parser to report formatters."""
    
    def run(self) :
        """Main entry point for the class."""
        
        # Command line parsing
        parser = optparse.OptionParser()
        parser.add_option('-i', '--pageid', 
                          dest="pageid", 
                          default=None,
                          type="int",
                          help=_("Page id to execute"),
                          )
        parser.add_option('-o', '--output',
                          dest="output_filename",
                          default=None,
                          action="store",
                          help=_("Report filename"),
                          )
        parser.add_option('-d', '--dir',
                          dest="output_directory",
                          default=None,
                          action="store",
                          help=_("Report folder name"),
                          )
        parser.add_option('-e', '--error-output',
                          dest="error_output_filename",
                          default=None,
                          action="store",
                          help=_("Error report filename"),
                          )
        parser.add_option('-f', '--filter', 
                          dest="filter", 
                          default=[],
                          type="string",
                          action="append",
                          help=_("Filter to execute only filtered tests"),
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
        parser.add_option('-n', '--dotnet',
                          dest="dotnet",
                          default=None,
                          action="store_true",
                          help=_(".Net execution"),
                          )
        parser.add_option('-s', '--shell',
                          dest="shell",
                          default=None,
                          action="store_true",
                          help=_("Execute command via shell"),
                          )
        parser.add_option('-O', '--command-line-output',
                          dest="commandline_output",
                          default=None,
                          action="store_true",
                          help=_("Show command line output"),
                          )
        options, remainder = parser.parse_args()

        if options.pageid is None :
            raise Exception(_("You must provide a valid page id"))
                        
        if not(options.lang is None):
            os.environ['LANGUAGE'] = options.lang
            gettext.install('greenrunner',os.path.join(os.path.dirname(sys.argv[0]),'locale'),unicode=True,names=['ngettext'])

        gp_parser = Parser()
        
        # The verbose mode can be changed from command line        
        gp_parser.set_verbose(options.verbose)
        
        # Login can be put in the configuration file, and overridden with the commande line.
        gp_parser.set_login( gp_parser.get_config('login') if (options.login is None) else options.login )
        
        # Password can be put in the configuration file, and overridden with the commande line.
        gp_parser.set_password( gp_parser.get_config('password') if (options.password is None) else options.password )
 
        # Green pepper root can be put in the configuration file, and overridden with the commande line.
        gp_parser.set_gproot( gp_parser.get_config('gproot') if (options.gproot is None) else options.gproot )

        # Green pepper command-line can be put in the configuration file, and overridden with the commande line.
        gp_parser.set_gp_commandline( gp_parser.get_config('commandline') if (options.commandline is None) else options.commandline )
        
        # Green pepper command-line is for .Net
        gp_parser.set_dotnet( gp_parser.get_config('dotnet') if (options.dotnet is None) else options.dotnet )
        
        # Use shell for commmand line
        gp_parser.set_shell( gp_parser.get_config('shell') if (options.shell is None) else options.shell )
        
        # Dump GP output into greenrunner output
        gp_parser.set_commandline_output( gp_parser.get_config('commandline_output') if (options.commandline_output is None) else options.commandline_output )
        
        
        
        self._report_generator = gp_parser.get_report_generator()

        # If output_filename is provided, we add a new FullReportFormatter
        if options.output_filename != None :
            self._report_generator.add_formatter(FullReportFormatter(options.output_filename))

        # If output_directory is provided, we add a new DirReportFormatter
        if options.output_directory != None :
            self._report_generator.add_formatter(DirReportFormatter(options.output_directory))

        # If error_output_filename is provided, we add a new ErrorReportFormatter
        if options.error_output_filename != None :
            self._report_generator.add_formatter(ErrorReportFormatter(options.error_output_filename))

        for filter_option in options.filter :
            for item in filter_option.split(',') :
                item = item.strip(' \r\n')
                try :
                    value = int(item)
                    gp_parser.add_numeric_filter(value)
                except :
                    if len(item)>0 :
                        gp_parser.add_title_filter(item)

        if not( gp_parser.run_tag_page( options.pageid ) ) :
            sys.exit(1)


    