###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["ResetPasswordWdg", "NewPasswordWdg", "ResetPasswordCmd", "NewPasswordCmd"]

import random
import hashlib

from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, Widget, WebContainer
from pyasm.widget import HiddenWdg, TextWdg, IconWdg, PasswordWdg, BaseSignInWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ActionButtonWdg
from pyasm.command import Command
from pyasm.common import TacticException
from pyasm.security import Batch, Login


class NewPasswordWdg(BaseSignInWdg):


    def get_content_styles(self):

        styles = HtmlElement.style('''

        .password-inputs {
            display: flex;
            flex-direction: column;
        }

        .password-inputs .sign-in-btn {
            align-self: center;
        }

        ''')

        return styles


    def get_content(self):
        
        web = WebContainer.get_web()
        login_name = web.get_form_value('login')
        hidden = HiddenWdg('login', login_name)

        div = DivWdg()
        div.add_style("margin: 0px 0px")
        div.add(hidden)


        # hidden element in the form to pass message that this was not
        # actually a typical submitted form, but rather the result
        # of a login page
        div.add( HiddenWdg("is_from_login", "yes") )
        div.add_style("font-size: 10px")

        login_div = DivWdg()
        div.add(login_div)
        login_div.add_class("password-inputs")

        password_container = DivWdg()
        login_div.add(password_container)
        password_container.add_class("sign-in-input")
        password_container.add("<div class='label'>Password</div>")

        password_wdg = PasswordWdg("my_password")
        password_container.add(password_wdg)

        confirm_password_container = DivWdg()
        login_div.add(confirm_password_container)
        confirm_password_container.add_class("sign-in-input")
        confirm_password_container.add("<div class='label'>Confirm Password</div>")

        confirm_password_wdg = PasswordWdg("confirm_password")
        confirm_password_container.add(confirm_password_wdg)

        reset_button = DivWdg('Reset')
        login_div.add(reset_button)
        reset_button.add_class("sign-in-btn hand")
        reset_button.add_attr('title', 'Reset Password')
        reset_button.add_event("onclick", "document.form.elements['new_password'].value='true'; document.form.submit()")

        hidden = HiddenWdg("new_password")
        login_div.add(hidden)

        div.add(self.get_content_styles())

        return div


class NewPasswordCmd(Command):


    def check(self):
        web = WebContainer.get_web()
        self.login = web.get_form_value("login")
        if self.login =='admin':
            error_msg = "You are not allowed to reset admin password."
            web.set_form_value(ResetPasswordWdg.MSG, error_msg)
            raise TacticException(error_msg)
            return False
        return True


    def execute(self):
        self.check()

        web = WebContainer.get_web()

        password = web.get_form_value("my_password")
        confirm_password = web.get_form_value("confirm_password")

        login = Login.get_by_login(self.login, use_upn=True)
        if not login:
            web.set_form_value(ResetPasswordWdg.MSG, 'This user [%s] does not exist or has been disabled. Please contact the Administrator.'%self.login)
            return  

        if password == confirm_password:
            encrypted = hashlib.md5(password).hexdigest()
            login.set_value('password', encrypted)
            login.commit()
        else:
            web.set_form_value(ResetPasswordWdg.MSG, 'The entered passwords do not match.')
            return



class ResetPasswordWdg(BaseSignInWdg):

    MSG = 'reset_msg'
    RESET_MSG = 'Reset completed.'

    def get_content_styles(self):

        styles = HtmlElement.style('''

            .reset-container {
                display: flex;
                flex-direction: column;
            }

            .sign-in-btn.email-reset-btn {
                align-self: flex-start;
            }

            .code-msg-container {
                margin: 20 0;
                color: #666;
                font-size: 12px;
                text-align: left;
            }

            .msg-user {
                text-decoration: underline;
            }

            .spt_code_div {
                display: flex;
                flex-direction: column;
            }

            ''')

        return styles


    def get_content(self):
        
        web = WebContainer.get_web()
        login_name = web.get_form_value('login')
        hidden = HiddenWdg('login', login_name)
     
        div = DivWdg()
        div.add_style("margin: 0px 0px")

        div.add(hidden)

        # hidden element in the form to pass message that this was not
        # actually a typical submitted form, but rather the result
        # of a login page
        div.add( HiddenWdg("is_from_login", "yes") )
        div.add_style("font-size: 10px")
        div.add_class("reset-container")

        reset_div = DivWdg()
        div.add(reset_div)
        reset_div.add_class("spt_reset_div")

        name_container = DivWdg()
        reset_div.add(name_container)
        name_container.add_class("sign-in-input")
        name_container.add("<div class='label'>Name</div>")

        name_wdg = TextWdg("reset_login")
        name_container.add(name_wdg)
        if login_name:
            name_wdg.set_value(login_name)

        # build the button manually
        email_reset_btn = DivWdg('Reset via Email')
        reset_div.add(email_reset_btn)
        email_reset_btn.add_class('sign-in-btn hand')
        email_reset_btn.add_attr('title', 'Reset via Email')
        email_reset_btn.add_event('onclick',"document.form.elements['send_code'].value='true'; document.form.submit()")

        hidden = HiddenWdg('send_code')
        div.add(hidden)
    
        #div.add(HiddenWdg(self.LOGIN_MSG))
        code_div = DivWdg()
        div.add(code_div)
        code_div.add_class("spt_code_div")

        code_div.add("<div class='code-msg-container'>A code was sent to <span class='msg-user'>%s</span>'s email. Please enter the code to reset your password:</div>" % login_name)
        
        code_container = DivWdg()
        code_div.add(code_container)
        code_container.add_class("sign-in-input")
        code_container.add("<div class='label'>Code</div>")

        code_wdg = TextWdg("code")
        code_container.add(code_wdg)

        next_button = DivWdg('Next')
        code_div.add(next_button)
        next_button.add_class('sign-in-btn hand')
        next_button.add_attr('title', 'Next')
        next_button.add_event("onclick", "document.form.elements['reset_password'].value='true'; document.form.submit()")

        hidden = HiddenWdg('reset_password')
        code_div.add(hidden)

        div.add(self.get_content_styles())
        
        return div



class ResetPasswordCmd(Command):

    def check(self):
        web = WebContainer.get_web()
        self.login = web.get_form_value("reset_login")
        if self.login =='admin':
            error_msg = "You are not allowed to reset admin password."
            web.set_form_value(ResetPasswordWdg.MSG, error_msg)
            raise TacticException(error_msg)
            return False
        return True

    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)
              
    def execute(self):
        # Since this is not called with Command.execute_cmd
        self.check()

        web = WebContainer.get_web()

        reset_on = self.kwargs.get('reset') == True
        if reset_on:
            security = WebContainer.get_security()
            #Batch()
            login = Login.get_by_login(self.login, use_upn=True)
            if not login:
                web.set_form_value(ResetPasswordWdg.MSG, 'This user [%s] does not exist or has been disabled. Please contact the Administrator.'%self.login)
                return
            email = login.get_value('email')
            if not email:
                web.set_form_value(ResetPasswordWdg.MSG, 'This user [%s] does not have an email entry for us to email you the new password. Please contact the Administrator.'%self.login)
                return

        
            # auto pass generation
            unique_code = ''.join([ random.choice('abcdefghijklmno12345') for i in xrange(0, 5)])
            auto_password = unique_code
            
            msg = ResetPasswordWdg.RESET_MSG
            
            # send the email
            try:
                from pyasm.command import EmailTriggerTestCmd

                admin = Login.get_by_login('admin')
                if admin:
                    sender_email = admin.get_full_email()
                    if not sender_email:
                        from pyasm.common import Config
                        sender_email = Config.get_value("services", "mail_default_admin_email")
                    else:
                        sender_email = 'support@southpawtech.com'
                recipient_emails = [email]
                email_msg = 'Your TACTIC password reset code is:\n\n%s' % auto_password
                email_cmd = EmailTriggerTestCmd(sender_email=sender_email, recipient_emails=recipient_emails, msg= email_msg, subject='TACTIC password change')

                data = login.get_json_value("data")
                data['temporary_code'] = auto_password
                login.set_json_value('data', data)
                login.commit()

                email_cmd.execute()

            except TacticException as e:
                msg = "Failed to send an email for your new password. Reset aborted."
                web.set_form_value(ResetPasswordWdg.MSG, msg)
                raise 
                
            # handle windows domains
            #if self.domain:
            #    self.login = "%s\\%s" % (self.domain, self.login)

            web.set_form_value(ResetPasswordWdg.MSG, msg)

     
