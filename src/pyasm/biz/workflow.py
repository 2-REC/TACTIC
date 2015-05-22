##########################################################
#
# Copyright (c) 2015, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['Workflow']

import tacticenv

from pyasm.common import Common
from pyasm.command import Trigger, Command
from pyasm.search import SearchType, Search, SObject
from pyasm.biz import Pipeline, Task
from tactic.command import PythonCmd


class Workflow(object):

    def init(my, startup=False):
        # initialize the triggers for the workflow
        event = "process|pending"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", ProcessPendingTrigger)
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=startup)

        event = "process|action"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", ProcessActionTrigger)
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=startup)


        event = "process|complete"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", ProcessCompleteTrigger)
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=startup)

        event = "process|approve"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", ProcessApproveTrigger)
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=startup)


        event = "process|revise"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", ProcessReviseTrigger)
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=startup)

        event = "process|error"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", ProcessErrorTrigger)
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=startup)

        # by default a stataus change to a trigger calls the node's trigger
        event = "change|sthpw/task|status"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", TaskStatusChangeTrigger)
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=startup)



class TaskStatusChangeTrigger(Trigger):

    def execute(my):

        # find the node in the pipeline
        task = my.get_caller()
        sobject = task.get_parent()
        if not sobject:
            return

        #print "status change: ", task.get_value("process"), task.get_value("status")

        pipeline = Pipeline.get_by_sobject(sobject)
        if not pipeline:
            return

        process_name = task.get_value("process")
        status = task.get_value("status")

        process = pipeline.get_process(process_name)
        node_type = process.get_type()
        process_name = process.get_name()

        event = "process|%s" % status.lower()
        output = {
            'sobject': sobject,
            'pipeline': pipeline,
            'process': process_name,
        }
        Trigger.call(task, event, output=output)

        




#
# Built in process triggers
#


class BaseProcessTrigger(Trigger):


    def set_all_tasks(my, sobject, process, status):
        tasks = Task.get_by_sobject(sobject, process=process)
        title = status.replace("-", " ")
        title = title.replace("_", " ")
        title = Common.get_display_title(title)
        for task in tasks:
            task.set_value("status", title)
            task.commit()
 

    def run_callback(my, pipeline, process, status):
        # get the node triggers
        # TODO: make this more efficient
        search = Search("config/process")        
        search.add_filter("pipeline_code", pipeline.get_code())
        search.add_filter("process", process)
        process_sobj = search.get_sobject()
        triggers = {}
        if process_sobj:
            triggers = process_sobj.get_json_value("trigger")
        if not triggers:
            triggers = {}

        ret_val = None

        action = triggers.get("on_%s" % status)
        action_path = triggers.get("on_%s_path" % status)

        kwargs, input = my.build_trigger_input()
        if action or action_path:
            if action:
                cmd = PythonCmd(code=action, input=input, **kwargs)
            else:
                cmd = PythonCmd(script_path=script_path, input=input, **kwargs)
            ret_val = cmd.execute()
        else:
            # or call a trigger
            event = "process|%s" % status

            # how to get the value here?
            triggers = Trigger.call(my, event, kwargs, process=process_sobj.get_code())
            if triggers:
                ret_val = triggers[0].get_ret_val()

        return ret_val



    def build_trigger_input(my):
        # create a package for the trigger

        pipeline = my.input.get("pipeline")
        process = my.input.get("process")
        sobject = my.input.get("sobject")



        kwargs = {
            'sobject': sobject,
            'pipreine': pipeline,
            'process': process
        }
        input = {
            'sobject': sobject.get_sobject_dict(),
            'pipeline': pipeline.to_string(),
            'process': process,
            'inputs': [x.get_name() for x in pipeline.get_input_processes(process)],
            'outputs': [x.get_name() for x in pipeline.get_output_processes(process)],
        }
        return kwargs, input



class ProcessPendingTrigger(BaseProcessTrigger):

    def execute(my):
        # set all task to pending

        pipeline = my.input.get("pipeline")
        process = my.input.get("process")
        sobject = my.input.get("sobject")


        process_obj = pipeline.get_process(process)
        node_type = process_obj.get_type()

        print "pending: ", process, node_type

        my.run_callback(pipeline, process, "pending")

        if node_type not in ["node", "manual"]:
            my.set_all_tasks(sobject, process, "pending")



        if node_type in ["auto", "condition"]:
            Trigger.call(my, "process|action", output=my.input)

        elif node_type in ["approval"]:

            # check to see if the tasks exist and if they don't then create one
            tasks = Task.get_by_sobject(sobject, process=process)
            if not tasks:
                tasks = Task.add_initial_tasks(sobject, processes=[process])
            else:
                print "tasks: ", tasks
                print tasks[0].get_data()
                my.set_all_tasks(sobject, process, "pending")


        elif node_type in ["heirarchy"]:
            child_pipeline = process_obj.get_child_pipeline()
            child_processes = child_pipeline.get_processes()
            if child_processes:
                first_process = child_processes[0]
                first_name = first_process.get_name()

                input = {
                        'pipeline': pipeline,
                        'sobject': sobject,
                        'process': first_process,
                }

                event = "process|pending"
                Trigger.call(my, "process|complete", input)





 

class ProcessActionTrigger(BaseProcessTrigger):

    def execute(my):

        # get the pipeline
        pipeline = my.input.get("pipeline")
        process = my.input.get("process")
        sobject = my.input.get("sobject")


        process_obj = pipeline.get_process(process)
        node_type = process_obj.get_type()

        print "action: ", process, node_type

        if node_type not in ["node", "manual", "approval"]:
            my.set_all_tasks(sobject, process, "in_progress")


        # get the node's triggers
        search = Search("config/process")        
        search.add_filter("process", process)
        process_sobj = search.get_sobject()
        triggers = {}
        if process_sobj:
            triggers = process_sobj.get_json_value("trigger")
        if not triggers:
            triggers = {}




        process_obj = pipeline.get_process(process)
        node_type = process_obj.get_type()

        if node_type == "condition":
            my.handle_condition_node(sobject, pipeline, process, triggers)

        elif node_type == "auto":

            action = triggers.get("action")
            action_path = triggers.get("action_path")
            kwargs, input = my.build_trigger_input()
            if action or action_path:
                if action:
                    cmd = PythonCmd(code=action, input=input, **kwargs)
                else:
                    cmd = PythonCmd(script_path=script_path, input=input, **kwargs)
                ret_val = cmd.execute()
            else:
                # or call a trigger
                Trigger.call(my, "process|action", input, process=process_sobj.get_code())

            Trigger.call(my, "process|complete", my.input)




            



    def handle_condition_node(my, sobject, pipeline, process, triggers):

        ret_val = my.run_callback(pipeline, process, "action")

        # if a None return value was given, then probably no condition exists
        # yet, so just let if flow through
        if ret_val == None:
            ret_val = True

        # run the completion trigger for this node
        Trigger.call(my, "process|complete", my.input)

        if ret_val == True:
            success_cbk = triggers.get("on_success")
            if success_cbk:
                cmd = PythonCmd(code=success_cbk, sobject=sobject)
                cmd.execute()
                return
            else:
                event = "process|pending"
                attr = "success"
                direction = "output"
                processes = pipeline.get_output_processes(process, from_attr=attr)
                if not processes:
                    attr = None

        elif ret_val == False:

            fail_cbk = triggers.get("on_fail")
            if fail_cbk:
                cmd = PythonCmd(code=fail_cbk, sobject=sobject)
                cmd.execute()
                return
            else:
                event = "process|revise"

                # check to see if there is an output process
                attr = "fail"
                processes = pipeline.get_input_processes(process, to_attr=attr)
                if processes:
                    direction = "output"
                else:
                    direction = "input"
                    attr = None

        else:
            event = "process|pending"
            if isinstance(ret_val, basestring): 
                ret_val = [ret_val]

            output_processes = []
            for attr in ret_val: 
                outputs = pipeline.get_output_processes(process, from_attr=attr)
                if outputs:
                    output_process.extend(outputs)

            # if there are no output attrs, then check the node names
            if not output_processes:
                outputs = pipeline.get_output_processes(process)
                for output in outputs:
                    if output.get_name() in ret_val:
                        output_processes.append(output)

            for output_process in output_processes:
                output_process_name = output_process.get_name()
                output = {
                    'sobject': sobject,
                    'pipeline': pipeline,
                    'process': output_process_name,
                }
                Trigger.call(my, event, output)

            return


        # by default, go back to incoming or outcoming
        if direction == "input":
            processes = pipeline.get_input_processes(process, to_attr=attr)
        else:
            processes = pipeline.get_output_processes(process, from_attr=attr)


        for process in processes:
            process_name = process.get_name()
            output = {
                'sobject': sobject,
                'pipeline': pipeline,
                'process': process_name,
            }
            Trigger.call(my, event, output)





class ProcessCompleteTrigger(BaseProcessTrigger):

    def get_status(my):
        return "complete"

    def execute(my):

        process = my.input.get("process")
        sobject = my.input.get("sobject")
        pipeline = my.input.get("pipeline")

        process_obj = pipeline.get_process(process)
        node_type = process_obj.get_type()
        print "complete: ", process, node_type

        status = my.get_status()

        # run a nodes complete trigger
        #event = "process|complete|%s" % process
        #Trigger.call(my, event, output=my.input)
        my.run_callback(pipeline, process, status)

        process_obj = pipeline.get_process(process)
        node_type = process_obj.get_type()

        if node_type in ["auto", "approval", "manual", "node"]:
            # call the process|pending event for all output processes
            output_processes = pipeline.get_output_processes(process)
            for output_process in output_processes:
                output_process = output_process.get_name()

                output = {
                    'pipeline': pipeline,
                    'sobject': sobject,
                    'process': output_process
                }

                event = "process|pending"
                Trigger.call(my, event, output)

        if node_type in ["auto", "condition"]:
            my.set_all_tasks(sobject, process, "complete")


        # if pipeline has a parent and this is the last node, then notify the
        # parent process
        #if pipeline.has_parent()?? and process == last_process:
        #    output = {
        #       'pipeline': parent_pipeline,
        #       'process': parent_process,
        #       'sobject': sobject
        #    }
        #    event = "process|complete"
        #    Trigger.call(my, event, input=output)


class ProcessApproveTrigger(ProcessCompleteTrigger):
    def get_status(my):
        return "approve"



class ProcessReviseTrigger(BaseProcessTrigger):

    def execute(my):

        process = my.input.get("process")
        sobject = my.input.get("sobject")
        pipeline = my.input.get("pipeline")

        process_obj = pipeline.get_process(process)
        node_type = process_obj.get_type()

        print "Revise: ", process, node_type

        #process = my.input.get("process")
        #my.run_callback(pipeline, process, "revise")

        if node_type in ['manual', 'node']:
            my.set_all_tasks(sobject, process, "revise")
        if node_type in ['auto']:
            my.set_all_tasks(sobject, process, "revise")

        if node_type in ['approval','auto','condition']:

            input_processes = pipeline.get_input_processes(process)
            for input_process in input_processes:
                input_process = input_process.get_name()

                input = {
                    'pipeline': pipeline,
                    'sobject': sobject,
                    'process': input_process
                }

                event = "process|revise"
                Trigger.call(my, event, input)





class ProcessErrorTrigger(BaseProcessTrigger):

    def execute(my):
        process = my.input.get("process")
        sobject = my.input.get("sobject")
        pipeline = my.input.get("pipeline")
 
        print "Error: Failed to process [%s] on sobject [%s]" % (process, sobject.get_search_key() )

        # TODO: send a message so that those following this sobject will be notified






