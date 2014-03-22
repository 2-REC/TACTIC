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

__all__ = ['Translation']

#import gettext
import os

from pyasm.common import Container
from pyasm.search import Search
from pyasm.biz import PrefSetting, TranslationSObj
from pyasm.biz import Translation as TranslationX

class Translation(object):

    def install(language=""):
        # get from preferences
        if not language:
            language = PrefSetting.get_value_by_key("language")

        # else get from project setting
        #if not language:
        #    from pyasm.prod.biz import ProdSetting
        #    language = ProdSetting.get_by_key("language")

        if os.environ.get("LC_MESSAGES"):
            language = os.environ.get("LC_MESSAGES")

        if os.environ.get("TACTIC_LANG"):
            language = os.environ.get("TACTIC_LANG")

        # else it is english
        if not language:
            language = "en"

        Container.put("language", language)

        # add some localization code
        #gettext.install("messages", unicode=True)
        #path = "%s/src/locale" % Environment.get_install_dir()
        #lang = gettext.translation("messages", localedir=path, languages=[language])
        #lang.install()

        # override the _ function
        import __builtin__
        __builtin__._ = Translation._translate

    install = staticmethod(install)



    def _translate(msg, language=None, chk=None):

        if not language:
            language = Container.get("language")

        sobject = TranslationX.get(language, msg)
        if sobject:

            if chk:
                chk = chk.strip("...")
                orig = sobject.get_value("en".lower())
                assert(orig)
                assert(orig.startswith(chk))

            msgstr = sobject.get_value(language)
            if not msgstr:
                return "No Translation"
            else:
                return msgstr

        if language != 'en':
            return "__%s__" % msg.upper()
        
        sobject = TranslationSObj.get(language, msg)
        if not sobject:
            return msg
        else:
            msgstr = sobject.get_value("msgstr")
            if not msgstr:
                return msg
            else:
                return msgstr
    _translate = staticmethod(_translate)


