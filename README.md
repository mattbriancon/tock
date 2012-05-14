
timetracker.py is a simple time program to help keep track of where you're spending your time.

Usage
========

start
------

Begin timing a new project.  If the project does not already exist it will be created.  If project is in progess, nothing happens.


stop
-----

Stop timing a project.  If the project does not already exist, nothing happens.  If the project is already stopped, nothing happens.


rm
-----

Remove a project.  User is prompted to confirm unless -f/--force option is used.  If project does not already exist, nothing happens.


list
-----

List all projects.


TODO
========

* Tests
* setup.py and everything else needed to be on PyPi
* View project history (as text and graphically)
* Project notes
* Integrate with PS1
