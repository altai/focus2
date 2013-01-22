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
require "find"
require "highline/import"
require "tmpdir"

task :default => [:hop]

desc "Run Python unittests"
task :test do
  system('python setup.py test')
end

desc "Run runserver"
task :run do
  system('python setup.py develop')
  system('export FOCUS2=`pwd`/local_settings.py && python -m focus2.runserver')
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


