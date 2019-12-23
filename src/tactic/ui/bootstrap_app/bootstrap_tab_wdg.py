
from pyasm.widget import WidgetConfig
from pyasm.web import DivWdg, HtmlElement

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import TabWdg

__all__ = ['BootstrapTabWdg']


class BootstrapTabWdg(BaseRefreshWdg):


    def init(self):
        
        config_xml = self.kwargs.get("config_xml")
        if not config_xml:
            config_xml = "<config><tab/></config>"
        
        view = "tab"
        config = WidgetConfig.get(view=view, xml=config_xml)
        
        self.tab = TabWdg(config=config, view=view, use_default_style=False, save_state="main_body_tab_state")
        self.unique_id = self.tab.get_tab_id()
        self.header_id = self.tab.get_header_id()
        

    def get_tab_id(self):
        return self.unique_id

    def get_header_id(self):
        return self.header_id

    def get_bootstrap_styles(self):

        header_id = self.get_header_id()
        style = """
            #%(header_id)s {
                display: none !important;
                background: var(--spt_palette_md_primary_light);
            }


            #%(header_id)s .spt_tab_header_label {
                color: var(--spt_palette_side_bar_title_color);
            }

            @media (min-width: 576px) {
                #%(header_id)s {
                    display: flex !important;
                }
            }
            


        """ % {'header_id': header_id}
            
        
        style += """
            .spt_tab_content_top[spt_tab_id="%(tab_id)s"] {
                overflow-y: auto;
                height: calc(100vh - 80px);
            }
            
            @media (max-width: 575.98px) {
                .spt_tab_content_top[spt_tab_id="%(tab_id)s"] {
                    height: 100%%;
                }
            }
            

        """ % {'tab_id': self.get_tab_id()}

        return HtmlElement.style(style)


    def get_display(self):

        top = self.top

        top.add(self.get_bootstrap_styles())

        top.add(self.tab)

        for widget in self.widgets:
            self.tab.add(widget)
        
        # HACK set the current one active
        div = DivWdg()
        div.add_behavior( {
        'type': 'load',
        'cbjs_action': '''
        spt.tab.set_main_body_top();
        var headers = spt.tab.get_headers();
        // if there are no headers, then there was an error
        if (headers.length == 0) {
            return;
        }

        var name = headers[headers.length-1].getAttribute("spt_element_name");
        spt.tab.select(name);
        '''
        } )
        top.add(div)

        return top
