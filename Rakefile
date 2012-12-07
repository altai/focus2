# Focus2
# Copyright (C) 2012 Grid Dynamics Consulting Services, Inc
# All Rights Reserved
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.

require "erb"
require "highline/import"
require "tmpdir"

task :default => [:test]

desc "Run Python unittests"
task :test do
  system('python setup.py test')
end

desc "Run runserver"
task :run do
  system('export FOCUS2=`pwd`/local_settings.py && python -m focus2.runserver')
end

namespace :bp do
  def test_filename(name)
    File.expand_path(File.join("tests", "test_" + name + ".py"))
  end
  
  desc 'Creates new blueprint'
  task :new do
    name = ask("Blueprint name? (valid module name):") do
      |q|
      q.validate = /^[a-z][a-z0-9_]*$/
    end
    url_prefix = ask("what is URL prefix? ") do
      |q|
      q.default = "/" + name.sub(/_/, "-")
      q.validate = /^\/.*[^\/]$/
    end
    has_static = agree("Has static folder?", true)
    has_templates = agree("Has templates fodler?", true)
  
    base = File.join(Dir.tmpdir, rand.to_s)
    mkdir base
    project = File.join(base, name)
    mkdir project
    template = ERB.new <<EOF
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Focus2
# Copyright (C) 2012 Grid Dynamics Consulting Services, Inc
# All Rights Reserved
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.


import flask

from flask import blueprints


"""
<%= "="*(name.length + " blueprint".length) %>
<%= name %> blueprint
<%= "="*(name.length + " blueprint".length) %>


"""

BP = blueprints.Blueprint('<%= name %>', __name__,<% if has_static then %>
                          static_folder='static',<% end %><% if has_templates then %>
                          template_folder='templates',
                          <% end %>url_prefix='<%= url_prefix %>')

# write your stuff here
EOF
    File.new(File.join(project, "__init__.py"), "w").write(template.result(binding))
    if has_static then
      static = File.join(project, "static")
      %w(css img js).each {|x| mkdir_p File.join(static, x)}
    end
    if has_templates then
      mkdir_p File.join(project, "templates", name, "haml")
    end
    mv project, File.expand_path("focus2/blueprints/")
    rm_r base

    template = ERB.new <<EOF
#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Focus2
# Copyright (C) 2012 Grid Dynamics Consulting Services, Inc
# All Rights Reserved
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.


import unittest
from focus2 import application_factory
EOF
    File.new(test_filename(name), "w").write(template.result(binding))
  end

  desc "Remove blueprint"
  task :rm do
    name = ask("Blueprint name?")
    bp_path = File.expand_path(File.join("focus2", "blueprints", name))
    if File.directory? bp_path then
      rm_r bp_path
    end
    test_path = test_filename(name)
    if File.file? test_path then
      rm_r test_path
    end
  end

end

namespace :js do

  desc "Watch JavaScript unittests with Testacular"
  task :unit do
    Dir.chdir "jstests"  do
      system "testacular start config.unit.js"
    end
  end

  desc "Watch JavaScript end-to-end tests with Testacular"
  task :e2e do
    Dir.chdir "jstests" do
      system "testacular start config.e2e.js"
    end
  end
end

namespace :repos do
  desc "Updates boostrap JS and LESS from the submodule"
  task :bootstrap do
    dest = File.expand_path "focus2/static/bootstrap/js/"
    mkdir_p dest
    Dir.chdir "bootstrap/js/" do
      cp Dir["bootstrap-*.js"], dest
    end
    dest = File.expand_path "focus2/static/bootstrap/less/"
    mkdir_p dest
    Dir.chdir "bootstrap/less/" do
      cp Dir["*.less"], dest
    end
    dest = File.expand_path "focus2/static/bootstrap/img/"
    mkdir_p dest
    Dir.chdir "bootstrap/img/" do
      cp Dir["*.png"], dest
    end
  end
end
