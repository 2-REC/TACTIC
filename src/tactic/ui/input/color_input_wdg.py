###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

# Color wheel input

__all__ = ['ColorWdg', 'ColorInputWdg', 'ColorContainerWdg']

from pyasm.common import Date, Common
from pyasm.web import Table, DivWdg, SpanWdg, WebContainer, Widget, HtmlElement
from pyasm.widget import IconWdg, IconButtonWdg, BaseInputWdg, TextWdg
from tactic.ui.common import BaseRefreshWdg

import random

from text_input_wdg import TextInputWdg



class ColorWdg(Widget):
    '''This is drawn once in the page to reuse by repositioning it'''
    def get_display(self):

        top = DivWdg()

        inner = DivWdg()
        top.add(inner)

        inner.add_style('position: absolute')
        inner.add_style('top: 100')
        inner.add_style('left: 100')
        inner.add_style("z-index: 1000")
        import random
        number = random.randint(1, 1000)
        rainbow_id = "rainbow_%s" % number
        inner.set_id(rainbow_id);

        #top.add('''
        #<img id="%s" src="/context/spt_js/mooRainbow/rainbow.png" alt="[r]" width="16" height="16" />
        #''' % rainbow_id)


        inner.add_behavior( { 
            "type": "load",
            'rainbow_id': rainbow_id,
            "cbjs_action": '''

            spt.color = {};
            spt.color.top = bvr.src_el;

            spt.color.init = function() {
                var js_file = "mooRainbow/Source/mooRainbow.js";
                var url = "/context/spt_js/" + js_file;
                var js_el = document.createElement("script");
                js_el.setAttribute("type", "text/javascript");
                js_el.setAttribute("src", url);
                var head = document.getElementsByTagName("head")[0];
                head.appendChild(js_el);

                setTimeout( function() {

                spt.color.rainbow = new MooRainbow(bvr.rainbow_id, {
                    id: bvr.rainbow_id,
                    startColor: [58, 142, 246],
                    imgPath:    '/context/spt_js/mooRainbow/Assets/images/',
                    onComplete: function(color) {
                        if (spt.color.rainbow){
                            var cbk = spt.color.rainbow.cbk;
                            cbk(color);
                        }
                    }
                });
                //make it rise above the Edit popup
                spt.color.rainbow.layout.setStyle('z-index','10000');
                spt.color.rainbow.spt_id = bvr.rainbow_id;

                }, 300 );

            }

            spt.color.get = function() {
                if (! spt.color.rainbow ) {
                    spt.color.init();
                }

                return spt.color.rainbow;
            }

            '''
        } )


        return inner


#
# Use this for input
#

class ColorInputWdg(BaseInputWdg):

    ARGS_KEYS = {
    }


    def __init__(self, name=None, **kwargs):
        if not name:
            name = kwargs.get("name")
        self.top = DivWdg()
        self.input = None
        self.kwargs = kwargs
        super(ColorInputWdg, self).__init__(name)

        if not self.input:
            self.input = TextInputWdg(name=self.get_input_name())



    def add_style(self, name, value=None):
        self.top.add_style(name, value)

    def set_input(self, input):
        self.input = input
        self.input.set_name(self.get_input_name() )

    def get_input(self):
        return self.input


    def add(self, widget):
        self.top.add(widget)


    def add_behavior(self, behavior):
        return self.input.add_behavior(behavior)



    def get_display(self):
        top = self.top


        value = self.get_value()
        if value:
            self.input.set_value(value)
            self.input.add_style("background", value)
        top.add(self.input)

        start_color = self.kwargs.get("start_color")

        if not value:
            if start_color and start_color.find(","):
                colors = start_color.split(",")

            elif not start_color or start_color == "random":
                #'rgba(188, 207, 215, 1.0)',
                colors = [
                    '#bccfd7',
                    '#bcd7cf',
                    '#d7bccf',
                    '#d7cfbc',
                    '#cfbcd7',
                    '#cfd7bc',
                ]

            import random
            num = random.randint(0,len(colors)-1)
            start_color = colors[num]
            #start_color = top.get_color(start_color, -10)


        if start_color:
            self.input.set_value(start_color)
            self.input.add_style("background", start_color)

        self.input.add_class("spt_color_input")
     
        if not start_color:
            start_color = [0, 0, 255]
        elif start_color.startswith("#"):
            start_color = start_color.replace("#", "")
            r, g, b = start_color[:2], start_color[2:4], start_color[4:]
            r, g, b = [int(n, 16) for n in (r, g, b)]

            start_color = [r, g, b]

        behavior = {
            'type': 'click_up',
            'name': self.get_name(),
            'start_color': start_color,
            'cbjs_action': '''

            var pos = bvr.src_el.getPosition();
            var input = bvr.src_el.getElement(".spt_color_input");
            var cell_edit = bvr.src_el.getParent(".spt_cell_edit");
            var current_color = input.value;
            input.setStyle("background-color", current_color);

            if (!current_color) {
                current_color = bvr.start_color;
            }
            else {
                var c = spt.css.convert_hex_to_rgb_obj(current_color);
                current_color = [c.r, c.g, c.b];
            }

            

            var options = {
                startColor: current_color,
                onComplete: function(color) {
                    input.value=color.hex;
                    
                }
            };

            var cbk = function(color) {
                input.value = color.hex;
                input.setStyle("background-color", color.hex);
                if (cell_edit) {
                    input.blur();
                    spt.table.accept_edit(cell_edit, input.value, true);
                }
                else {
                    input.focus();
                    input.blur();
                }
            };

            var rainbow = null;
            var rainbow = spt.color.get();
            // function to actually display the mooRainbow picker
            var display_dialog = function() {

                rainbow.cbk = cbk;
                rainbow.manualSet( current_color );

                // set the position
                spt.color.top.setStyle('left', pos.x);
                spt.color.top.setStyle('top', pos.y+20);
                //spt.color.top.setStyle('z-index', '1000');
                rainbow.show();
            }
        
            if (rainbow) {
                display_dialog();
            } else { // this could be run at the very first time it is drawn
                setTimeout(function() {
                rainbow = spt.color.get();
                display_dialog();
            
                }, 1000)
            }
            '''
        }
        top.add_behavior(behavior)

        return top



class ColorContainerWdg(BaseRefreshWdg):

    def __init__(self, **kwargs):
        super(ColorContainerWdg,self).__init__()

        from pyasm.widget import ColorWdg
        self.color_wdg = ColorWdg(kwargs)


    def get_styles(self):

        styles = HtmlElement.style('''

            .spt_color_container {
                height: 40px;
                width: 84;
                position: relative;
            }

            .spt_color_value {
                height: 100%;
                width: 100%;
            }

            .spt_color_label {
                position: absolute;
                top: 12px;
                left: 12px;
                font-size: 14px;
                color: white;
            }

            ''')

        return styles


    def get_display(self):

        top = DivWdg()
        top.add_class("spt_color_container")

        top.add(self.color_wdg)
        self.color_wdg.add_class("spt_color_value")
        self.color_wdg.add_behavior({
            'type': 'change',
            'cbjs_action': '''

            /* hexToComplimentary : Converts hex value to HSL, shifts
             * hue by 180 degrees and then converts hex, giving complimentary color
             * as a hex value
             * @param  [String] hex : hex value  
             * @return [String] : complimentary color as hex value
             */
            function hexToComplimentary(hex){

                // Convert hex to rgb
                // Credit to Denis http://stackoverflow.com/a/36253499/4939630
                var rgb = 'rgb(' + (hex = hex.replace('#', '')).match(new RegExp('(.{' + hex.length/3 + '})', 'g')).map(function(l) { return parseInt(hex.length%2 ? l+l : l, 16); }).join(',') + ')';

                // Get array of RGB values
                rgb = rgb.replace(/[^\d,]/g, '').split(',');

                var r = rgb[0], g = rgb[1], b = rgb[2];

                // Convert RGB to HSL
                // Adapted from answer by 0x000f http://stackoverflow.com/a/34946092/4939630
                r /= 255.0;
                g /= 255.0;
                b /= 255.0;
                var max = Math.max(r, g, b);
                var min = Math.min(r, g, b);
                var h, s, l = (max + min) / 2.0;

                if(max == min) {
                    h = s = 0;  //achromatic
                } else {
                    var d = max - min;
                    s = (l > 0.5 ? d / (2.0 - max - min) : d / (max + min));

                    if(max == r && g >= b) {
                        h = 1.0472 * (g - b) / d ;
                    } else if(max == r && g < b) {
                        h = 1.0472 * (g - b) / d + 6.2832;
                    } else if(max == g) {
                        h = 1.0472 * (b - r) / d + 2.0944;
                    } else if(max == b) {
                        h = 1.0472 * (r - g) / d + 4.1888;
                    }
                }

                h = h / 6.2832 * 360.0 + 0;

                // Shift hue to opposite side of wheel and convert to [0-1] value
                h+= 180;
                if (h > 360) { h -= 360; }
                h /= 360;

                // Convert h s and l values into r g and b values
                // Adapted from answer by Mohsen http://stackoverflow.com/a/9493060/4939630
                if(s === 0){
                    r = g = b = l; // achromatic
                } else {
                    var hue2rgb = function hue2rgb(p, q, t){
                        if(t < 0) t += 1;
                        if(t > 1) t -= 1;
                        if(t < 1/6) return p + (q - p) * 6 * t;
                        if(t < 1/2) return q;
                        if(t < 2/3) return p + (q - p) * (2/3 - t) * 6;
                        return p;
                    };

                    var q = l < 0.5 ? l * (1 + s) : l + s - l * s;
                    var p = 2 * l - q;

                    r = hue2rgb(p, q, h + 1/3);
                    g = hue2rgb(p, q, h);
                    b = hue2rgb(p, q, h - 1/3);
                }

                r = Math.round(r * 255);
                g = Math.round(g * 255); 
                b = Math.round(b * 255);

                // Convert r b and g values to hex
                rgb = b | (g << 8) | (r << 16); 
                return "#" + (0x1000000 | rgb).toString(16).substring(1);
            }

            function lightOrDark(color) {
                // Variables for red, green, blue values
                var r, g, b, hsp;
                
                // Check the format of the color, HEX or RGB?
                if (color.match(/^rgb/)) {

                    // If HEX --> store the red, green, blue values in separate variables
                    color = color.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*(\d+(?:\.\d+)?))?\)$/);
                    
                    r = color[1];
                    g = color[2];
                    b = color[3];
                } 
                else {
                    
                    // If RGB --> Convert it to HEX: http://gist.github.com/983661
                    color = +("0x" + color.slice(1).replace( 
                    color.length < 5 && /./g, '$&$&'));

                    r = color >> 16;
                    g = color >> 8 & 255;
                    b = color & 255;
                }
                
                // HSP (Highly Sensitive Poo) equation from http://alienryderflex.com/hsp.html
                hsp = Math.sqrt(
                0.299 * (r * r) +
                0.587 * (g * g) +
                0.114 * (b * b)
                );

                // Using the HSP value, determine whether the color is light or dark
                if (hsp>127.5) {

                    return 'light';
                } 
                else {

                    return 'dark';
                }
            }

            var hex = bvr.src_el.value;
            //var complimentary = hexToComplimentary(hex);
            var isLight = lightOrDark(hex) == 'light';
            var textColor = isLight ? '#000000' : '#ffffff';

            console.log(hex, "hecks", isLight);

            var top = bvr.src_el.getParent(".spt_color_container");
            var label = top.getElement(".spt_color_label");

            label.innerText = hex;
            label.setStyle("color", textColor);

            '''
        })

        color_label = DivWdg("#000000")
        top.add(color_label)
        color_label.add_class("spt_color_label")

        top.add(self.get_styles())

        return top






