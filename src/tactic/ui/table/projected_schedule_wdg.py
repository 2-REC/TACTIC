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

__all__ = ['ProjectedCompletionWdg', 'GetProjectedScheduleCmd', 'WorkflowSchedulePreviewWdg']

import six
from dateutil import parser
from datetime import datetime
from pyasm.biz import TaskGenerator, Pipeline, Project
from pyasm.common import SPTDate, Environment
from pyasm.command import Command
from pyasm.web import DivWdg, HtmlElement
from pyasm.search import Search, SearchType

from tactic.ui.common import BaseTableElementWdg, BaseRefreshWdg

from tactic.ui.panel import ViewPanelWdg
import datetime


class WorkflowSchedulePreviewWdg(BaseRefreshWdg):
    '''Create a schedule preview for workflow created'''
    ARGS_KEYS = {
        'pipeline_code': {
            'description': 'the code of the pipeline that is previewing',
            'type': 'string'
        }
    }

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.pipeline_code = self.kwargs.get("pipeline_code")

    def get_styles(self):
        style = HtmlElement.style('''
        .spt_schedule_preview_top {
            padding: 3px 5px;

        }

        .spt_schedule_preview_title {
            font-size: 25px;
            padding: 5px 0px 0px 10px;
            font-weight: bold
        }
        ''')

        return style
    
    def get_display(self):
        top = DivWdg()
        style = self.get_styles()
        top.add(style)
        top.add_class("spt_schedule_preview_top")
        title = DivWdg("Schedule Preview")
        title.add_class("spt_schedule_preview_title")
        top.add(title)
        top.add("<hr/>")

        search = Search('sthpw/pipeline')
        search.add_filter("code", self.pipeline_code)
        self.pipeline = search.get_sobject()

        process_s = Search("config/process")
        process_s.add_filter("pipeline_code", self.pipeline_code)
        processes = process_s.get_sobjects()

        processes = {x.get_value("process"): x for x in processes}

        today = datetime.datetime.today()
        login = Environment.get_user_name()

        job = SearchType.create('workflow/job')
        job.set_value("pipeline_code", self.pipeline_code)
        job.set_value('job_code', 'TMP00001')
        job.set_value('login', login)
        
        generator = TaskGenerator(generate_mode="schedule")
        tasks = generator.execute(
            job,
            self.pipeline, 
            start_date=today,
            today=today,
            process_sobjects=processes
        )
        completion_date = generator.get_completion_date()


        start_date = today
        due_date = completion_date

        special_days = []
        if start_date:
            special_days.append({
                "name": "Start Date",
                "date": start_date.strftime("%Y-%m-%d"),
                "color": "rgba(255,0,0,0.1)",
            })
        if due_date:
            special_days.append({
                "name": "Due Date",
                "date": due_date.strftime("%Y-%m-%d"),
                "color": "rgba(255,0,0.1)",
            })

        milestones = Search.eval("@SOBJECT(sthpw/milestone['project_code','$PROJECT'])")
        for milestone in milestones:
            special_days.append( {
                "name": milestone.get_value("description"),
                "date": milestone.get_datetime_value("due_date").strftime("%Y-%m-%d"),
                "color": "rgba(0,255,0,0.1)"
            } )

        kwargs = {
            'layout': 'spt.tools.gantt.GanttLayoutWdg',
            'mode': 'preview',
            'search_type': 'sthpw/task',
            'settings': 'keyword_search|save|search_limit',
            'simple_search_view': 'task_filter',
            'sobjects': tasks,
            'show_context_menu': False,
            'show_layout_switcher': False,
            'show_help': False,
            'order_by': 'search_code,bid_start_date,bid_end_date',
            'search_view': 'link_search:job_tasks',
            'element_names': 'process,status,assigned,days_due,description',
            'extra_data': {"single_line": "true"},
            'special_days': special_days,
            'init_load_num': len(tasks),
            'processes': processes
        }
        table = ViewPanelWdg(**kwargs)

        top.add(table)


        return top


class ProjectedCompletionWdg(BaseTableElementWdg):
    '''predicts completion date of sobject'''

    ARGS_KEYS = {
        'start_column': {
            'description': 'Column for schedule start date',
            'type': 'TextWdg',
            'order': '01'
        },
    }


    def init(self):
        self.dates = {}


    def is_editable(cls):
        return False
    is_editable = classmethod(is_editable)


    def get_data(self):

        tasks_by_code = {}
        pipelines_by_code = {}
        processes_by_pipeline = {}
        
        get_data = True
        if not get_data:
            return tasks_by_code, pipelines_by_code, processes_by_pipeline
        
        # Get tasks, pipelines and process sobjects.
        task_s = Search("sthpw/task")
        task_s.add_sobjects_filter(self.sobjects)
        tasks = task_s.get_sobjects()

        pipeline_s = Search("sthpw/pipeline")
        pipeline_codes = [x.get_value("pipeline_code") for x in self.sobjects]
        pipeline_s.add_filters("code", pipeline_codes)
        pipelines = pipeline_s.get_sobjects()

        process_s = Search("config/process")
        process_s.add_filters("pipeline_code", pipeline_codes)
        processes = process_s.get_sobjects()

        for task in tasks:
            search_code = task.get_value("search_code")
            if not tasks_by_code.get(search_code):
                tasks_by_code[search_code] = [task]
            else:
                tasks_by_code[search_code].append(task)

        for pipeline in pipelines:
            code = pipeline.get_code()
            pipelines_by_code[code] = pipeline
        
        for process in processes:
            pipeline_code = process.get_value("pipeline_code")
            if not processes_by_pipeline.get(pipeline_code):
                processes_by_pipeline[pipeline_code] = [process]
            else:
                processes_by_pipeline[pipeline_code].append(process)
            
        for pipeline_code in processes_by_pipeline:
            process_sobjects = {}
            processes = processes_by_pipeline.get(pipeline_code)
            for sobj in processes:
                process = sobj.get_value("process")
                process_sobjects[process] = sobj
            processes_by_pipeline[pipeline_code] = process_sobjects

        return tasks_by_code, pipelines_by_code, processes_by_pipeline


    def preprocess(self):

        start_column = self.kwargs.get("start_column")
        if not start_column:
            start_column = "start_date"
        
        tasks_by_code, pipelines_by_code, processes_by_pipeline = self.get_data()
        for sobj in self.sobjects:
        
            tasks = tasks_by_code.get(sobj.get_code())
            pipeline = pipelines_by_code.get(sobj.get_value("pipeline_code"))
            process_sobjects = processes_by_pipeline.get(pipeline.get_code())

            start_date = sobj.get_value(start_column)
            
            cmd = GetProjectedScheduleCmd(
                sobject=sobj,
                pipeline=pipeline,
                process_sobjects=process_sobjects,
                start_date=start_date,
                tasks=tasks
            )
            completion_date = cmd.execute().get("completion_date")
            self.dates[sobj.get_search_key()] = completion_date


    def get_display(self):
        
        sobject = self.get_current_sobject()
 
        value = self.dates.get(sobject.get_search_key())
        if value:
            value = SPTDate.get_display_date(value) 
        if not value:
            value = ""
         
        value_wdg = DivWdg()
        value_wdg.add(value)
        return value_wdg



class GetProjectedScheduleCmd(Command):

    def execute(self):
        '''Calculates the projected schedule for a given sobject'''
        sobject = self.kwargs.get("sobject")
        pipeline = self.kwargs.get("pipeline")
        tasks = self.kwargs.get("tasks")
        process_sobjects = self.kwargs.get("process_sobjects")

        if not pipeline:
            pipeline = Pipeline.get_by_sobject(sobject)

        completion_date = ""
        tasks = []

        if pipeline: 
            start_date = self.kwargs.get("start_date")
            today = self.kwargs.get("today") or datetime.today()
            
            if isinstance(start_date, six.string_types):
                start_date = parser.parse(start_date)
            
            if isinstance(today, six.string_types):
                today = parser.parse(today)
                

            generator = TaskGenerator(generate_mode="projected_schedule")
            tasks = generator.execute(
                sobject, 
                pipeline, 
                start_date=start_date, 
                today=today,
                existing_tasks=tasks,
                process_sobjects=process_sobjects
            )
            completion_date = generator.get_completion_date()
            
        self.info = {
            'completion_date': completion_date,
            'tasks': tasks        
        }
        return self.info
