
<p align="center">
  <img width="400px" src="http://community.southpawtech.com/tactic/plugins/community/theme/media/TACTIC_logo.svg"/>
</p>

<p align="center">
  <img width="400px" src="http://community.southpawtech.com/tactic/plugins/community/content/media/Showreel.gif"/>
</p>


## Workflow Platform

TACTIC is a comprensive, open-source platform for creating and executing digital workflows.  TACTIC has been used in many exciting projects in a wide variety on industries.

<p align="center">
  <img width="75%" src="https://southpawtech.com/wp-content/uploads/2020/03/online_workflow-1024x480.png"/>
</p>


## Features

TACTIC has a number of key components:

* Workflow Engine and Manager:
* Data Management
* File System Management
* Web Framework

## Installation

You can download the latest distributions from any of number of formats from the [community downloads](http://community.southpawtech.com/community/link/downloads) 

or you can access [earlier versions](http://community.southpawtech.com/downloads)

For detailed installation instructions, the [TACTIC System Administration](http://community.southpawtech.com/docs/sys-admin/) documentation is useful


## Getting Started

Getting started is easy.  You can start up quickly with an official VM distribution which has the database and webserver all setup for you.  Refer to the [Quick Start Guide](http://community.southpawtech.com/docs/quick-start/) for more information:


## Documentation

Detailed [documentation](http://community.southpawtech.com/community/link/docs/) can be found on the community site.

There documentation is split in different sections that focus on different aspects of TACTIC:

1. [Quick Start](http://community.southpawtech.com/docs/quick-start/): quick overview of how what to do to get up and running
1. [System Administration](http://community.southpawtech.com/docs/sys-admin/): detailed description of installation and connections to database and other external services.
1. [Setup](http://community.southpawtech.com/docs/setup/): description of how to set up a TACTIC project for end users to work on.
1. [Developer](http://community.southpawtech.com/docs/developer/): documention for developers to customize TACTIC and access the API.




## API

TACTIC has a very deep and mature API allow you to customize almost any part of the system.

Python Example
```python
from tactic_client_lib import TacticServerStub.get()
server = TacticServerStub.get()
shots = server.query("vfx/shot", ['sequence_code', 'SEQ001'])
for shot in shots:
    print("shot: ", shot.get("status") )
```

Javascript Example
```javascript
let server = TACTIC.get();
server.update(shot_key, {'status', 'Complete'})
```

Complete documentation can be found on the [TACTIC Developer Documentation](http://community.southpawtech.com/docs/developer)

## Resources

For more information, visit the community site for TACTIC:

http://tactic.southpawtech.com


Or participate in the forum if you have any questions:

http://forum.southpawtech.com



## Visual Effects (VFX)

TACTIC has a built-in VFX module that has been used as a template for countless productions around the world.  Over the years, it's popularity has grown considerably and more and more people become familiar with TACTIC features.  Because TACTIC is Open Source, it can configured and connected seamleassly into any studio producing content.


<p align="center">
  <img width="75%" src="doc/github/images/vfx_data_model.png"/>
</p>

Easily start up your production by creating a project with TACTIC nad selecting the VFX template.  Create your own template and reuse your own template for all future productions.

## License

[Eclipse Public License 1.0](LICENSE)
