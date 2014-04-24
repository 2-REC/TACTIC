###########################################################
#
# Copyright (c) 2014, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['GalleryWdg']

from pyasm.biz import Snapshot, File
from pyasm.search import Search
from pyasm.web import HtmlElement, DivWdg, Table
from pyasm.widget import TextWdg, IconWdg

from tactic.ui.common import BaseRefreshWdg



class GalleryWdg(BaseRefreshWdg):

    def get_display(my):

        my.sobject_data = {}

        top = my.top
        top.add_style
        top.add_class("spt_gallery_top")

        inner = DivWdg()
        top.add(inner)
        inner.add_style("position: fixed")
        inner.add_style("top: 0")
        inner.add_style("left: 0")
        inner.add_style("width: 100%")
        inner.add_style("height: 100%")
        #inner.add_style("background: rgba(0,0,0,0.5)")
        inner.add_style("background: rgba(0,0,0,1)")
        inner.add_style("z-index: 1000")
        """
        inner.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_gallery_top");
            spt.behavior.destroy_element(top);
            '''
        } )
        """


        icon = IconWdg(title="Close", icon="/plugins/remington/pos/icons/close.png")
        inner.add(icon)
        icon.add_style("position: absolute")
        icon.add_style("cursor: pointer")
        icon.add_style("bottom: 0px")
        icon.add_style("right: 0px")
        icon.add_behavior( {
            'type': 'click_up' ,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_gallery_top");
            spt.behavior.destroy_element(top);
            '''
        } )


        icon = IconWdg(title="Previous", icon="/plugins/remington/pos/icons/chevron_left.png")
        inner.add(icon)
        icon.add_style("cursor: pointer")
        icon.add_style("position: absolute")
        icon.add_style("top: 40%")
        icon.add_style("left: 0px")
        icon.add_behavior( {
            'type': 'click_up' ,
            'cbjs_action': '''
            spt.gallery.show_prev(); 
            '''
        } )


        icon = IconWdg(title="Next", icon="/plugins/remington/pos/icons/chevron_right.png")
        inner.add(icon)
        icon.add_style("position: absolute")
        icon.add_style("cursor: hand")
        icon.add_style("top: 40%")
        icon.add_style("right: 0px")
        icon.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.gallery.show_next(); 
            '''
        } )


        width = my.kwargs.get("width")
        height = my.kwargs.get("height")
        if not width:
            width = 1024


        paths = my.get_paths()

        descriptions = [ my.sobject_data.get(x).get("description") for x in paths]
        inner.add_behavior( {
        'type': 'load',
        'width': width,
        'descriptions': descriptions,
        'cbjs_action': '''

        spt.gallery = {};

        spt.gallery.top = bvr.src_el;
        spt.gallery.width = bvr.width;
        spt.gallery.content = spt.gallery.top.getElement(".spt_gallery_content");
        spt.gallery.desc_el = spt.gallery.top.getElement(".spt_gallery_description");
        spt.gallery.descriptions = bvr.descriptions;
        spt.gallery.index = 0;
        spt.gallery.total = bvr.descriptions.length;

        spt.gallery.init = function() {
            
        }

        spt.gallery.stack = [];

        spt.gallery.push_stack = function(key) {
            spt.gallery.stack.push(key);
        }


        spt.gallery.show_next = function() {
            if (spt.gallery.index == spt.gallery.total-1) {
                return;
            }
            spt.gallery.index += 1;
            spt.gallery.show_index(spt.gallery.index);
        }

        spt.gallery.show_prev = function() {
            if (spt.gallery.index == 0) {
                return;
            }
            spt.gallery.index -= 1;
            spt.gallery.show_index(spt.gallery.index);
        }


        spt.gallery.show_index = function(index) {
            var width = spt.gallery.width;
            var margin = - width * index;
            var content = spt.gallery.content;
            //content.setStyle("margin-left", margin + "px");
            new Fx.Tween(content,{duration: 250}).start("margin-left", margin);

            spt.gallery.index = index;

            var description = spt.gallery.descriptions[index];
            var total = spt.gallery.total-1;
            if (!description) {
                description = "("+index+" of "+total+")";
            }
            else {
                description = "("+(index+1)+" of "+total+") - " + description;
            }
            spt.gallery.set_description(description);
        }


        spt.gallery.close = function() {
            var content = spt.gallery.content;
            var top = content.getParent(".spt_gallery_top");
            spt.behavior.destroy_element(top);
        }


        spt.gallery.set_description = function(desc) {
            var desc_el = spt.gallery.desc_el;
            desc_el.innerHTML = desc;
        }

        '''
        } )




        desc_div = DivWdg()
        desc_div.add_class("spt_gallery_description")
        desc_div.add_style("height: 30px")
        desc_div.add_style("width: %s" % width)
        desc_div.add_style("text-align: center")
        desc_div.add_style("background: rgba(255,255,255,0.8)")
        desc_div.add_style("color: #000")
        desc_div.add_style("font-weight: bold")
        desc_div.add_style("font-size: 1.2em")
        desc_div.add_style("padding-top: 3px")
        desc_div.add_style("margin-left: -%s" % (width/2))
        desc_div.add("")

        desc_outer_div = DivWdg()
        inner.add(desc_outer_div)
        desc_outer_div.add_style("position: fixed")
        desc_outer_div.add(desc_div)
        desc_outer_div.add_style("bottom: 0px")
        desc_outer_div.add_style("left: 50%")





        scroll = DivWdg()
        inner.add(scroll)
        scroll.set_box_shadow()

        scroll.add_style("width: %s" % width)
        if height:
            scroll.add_style("height: %s" % height)
        scroll.add_style("overflow-x: hidden")
        scroll.add_style("overflow-y: hidden")
        scroll.add_style("background: #000")

        #scroll.add_style("position: absolute")
        scroll.add_style("margin-left: auto")
        scroll.add_style("margin-right: auto")



        total_width = width * len(paths)

        content = DivWdg()
        scroll.add(content)
        content.add_class("spt_gallery_content")

        content.add_style("width: %s" % total_width)

        scroll.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            bvr.src_el.getElement(".spt_input").focus();
            '''
        } )
 
        scroll.add_behavior( {
            'type': 'mouseenter',
            'cbjs_action': '''
            bvr.src_el.getElement(".spt_input").focus();
            '''
        } )
        scroll.add_behavior( {
            'type': 'mouseleave',
            'cbjs_action': '''
            bvr.src_el.getElement(".spt_input").blur();
            '''
        } )



        input = TextWdg("keydown")
        content.add(input)
        input.add_style("position: absolute")
        input.add_style("left: -5000px")

        input.add_behavior( {
            'type': 'keydown',
            'width': width,
            'cbjs_action': '''
            var key = evt.key;
            if (key == "left") {
                spt.gallery.push_stack(key);
                spt.gallery.show_prev();
            }
            else if (key == "right") {
                spt.gallery.push_stack(key);
                spt.gallery.show_next();
            }
            else if (key == "esc" || key == "enter") {
                var top = bvr.src_el.getParent(".spt_gallery_top");
                spt.behavior.destroy_element(top);
            }



            '''
        } )



        curr_index = 0
        for i, path in enumerate(paths):
            path_div = DivWdg()
            content.add(path_div)
            path_div.add_style("float: left")

            if path == my.curr_path:
                curr_index = i

            path_div.add_style("width: %s" % width)
            if height:
                path_div.add_style("height: %s" % height)

            from tactic.ui.widget import EmbedWdg
            embed = EmbedWdg(src=path)
            path_div.add(embed)
            embed.add_style("width: 100%")

            #img = HtmlElement.img(path)
            #path_div.add(img)
            #img.add_style("width: 100%")



        content.add_behavior({
            'type': 'load',
            'index': curr_index,
            'cbjs_action': '''
            if (!bvr.index) bvr.index = 0;
            spt.gallery.show_index(bvr.index);
            '''
        } )


        return top



    def get_paths(my):

        search_key = my.kwargs.get("search_key")
        if search_key:
            sobject = Search.get_by_search_key(search_key)
            snapshot = Snapshot.get_latest_by_sobject(sobject)
            file_object = File.get_by_snapshot(snapshot)[0]
            my.curr_path = file_object.get_web_path()
        else:
            my.curr_path = None

        search_keys = my.kwargs.get("search_keys")
        paths = my.kwargs.get("paths")

        if search_keys:
            sobjects = Search.get_by_search_keys(search_keys)
            snapshots = Snapshot.get_by_sobjects(sobjects)
            file_objects = File.get_by_snapshots(snapshots, file_type='main')
            paths = [x.get_web_path() for x in file_objects]

            for sobject, path in zip(sobjects, paths):
                my.sobject_data[path] = sobject

                

        elif paths:
            return paths

        else:
            # TEST
            paths = [
                '/assets/test/store/The%20Boxter_v001.jpg',
                '/assets/test/store/Another%20one_v001.jpg',
                '/assets/test/store/Whatever_v001.jpg'
            ]

        return paths




