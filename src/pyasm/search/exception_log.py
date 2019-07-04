###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['ExceptionLog']

from pyasm.common import *
from search import *
from sql import DbContainer

import sys,traceback

class ExceptionLog(SObject):
    '''Class that controls the logging of all of the exceptions that occur
    during the Tactic runtime'''


    def log(exception, message=None):
        
        tb = sys.exc_info()[2]
        stacktrace = traceback.format_tb(tb)
        stacktrace_str = "".join(stacktrace)

        # replace crazy windows paths with normal paths
        stacktrace_str = stacktrace_str.replace("\\", "/")

        print("-"*50)
        print("From ExceptionLog.log")
        print("-"*50)
        print(stacktrace_str)
        print(str(exception))
        print("-"*50)

        # make sure all of the databases are rolled back
        DbContainer.rollback_all()

        # record the exception
        user_name = Environment.get_user_name()
        if not user_name:
            user_name = "UNKNOWN"

        if not message:
            message = str(exception)

        class_name = exception.__class__.__name__

        from pyasm.security import Sudo
        sudo = Sudo()
        try:
            exception_log = SObjectFactory.create("sthpw/exception_log")
            exception_log.set_value("login", user_name)
            exception_log.set_value("class", class_name)
            exception_log.set_value("message", message)
            exception_log.set_value("stack_trace", stacktrace_str)
            exception_log.commit()
        finally:
            sudo.exit()

        del tb, stacktrace
       
        sender_email = Config.get_value("services", "notify_user")
        if sender_email:
            
            from pyasm.security import Site
            site = Site.get_site()

            sender_name = Config.get_value("services", "notify_user_name")
            recipient_emails = [sender_email]
            message = """
An exception has been reported in the TACTIC Exception Log.
           
Site: %s
Login: %s
Class: %s
Message: 
            
%s
            
Stack trace: 
            
%s
            """ % (site, user_name, class_name, message, stacktrace_str)
            
            exception_code = exception_log.get_code()
            subject = "New TACTIC Exception Log from %s [%s]" % (user_name, exception_code)
            
            from pyasm.command import SendEmail
            email_cmd = SendEmail(
                sender_email=sender_email,
                recipient_emails=recipient_emails,
                msg=message,
                subject=subject,
                sender_name=sender_name,
                log_exception=False
            )
            email_cmd.execute()


        return exception_log

    log = staticmethod(log)


    def get_stack_trace(exception):
        tb = sys.exc_info()[2]
        stacktrace = traceback.format_tb(tb)
        stacktrace_str = "".join(stacktrace)

        # replace crazy windows paths with normal paths
        stacktrace_str = stacktrace_str.replace("\\", "/")
        return stacktrace_str
    get_stack_trace = staticmethod(get_stack_trace)


